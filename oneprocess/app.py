import streamlit as st
import pandas as pd
import io
from oneprocess.core.processor import DataProcessor
from oneprocess.visuals.charts import GraphAnalyzer

st.set_page_config(page_title="OneProcess - Data Toolkit", layout="wide", page_icon="⚡")

st.title("⚡ OneProcess")
st.caption("A Unified Data Processing, Cloud Ingestion, and Analytics Toolkit")

# Sidebar file uploader for active workspace
# Sidebar file uploader for active workspace
st.sidebar.header("📁 Primary Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

# Initialize session state keys
if "df" not in st.session_state:
    st.session_state.df = None
if "original_df" not in st.session_state:
    st.session_state.original_df = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# Only load when a file is uploaded AND it's new/changed
if uploaded_file is not None:
    if st.session_state.last_uploaded_file != uploaded_file.name:
        loaded_df = DataProcessor.read_file(uploaded_file)
        
        # Save both current working copy and original backup
        st.session_state.df = loaded_df
        st.session_state.original_df = loaded_df.copy()
        st.session_state.last_uploaded_file = uploaded_file.name
        st.session_state.last_action = None

    if st.session_state.df is not None:
        st.sidebar.success(f"Loaded: {st.session_state.df.shape[0]} rows, {st.session_state.df.shape[1]} cols")
else:
    # Clear state if user removes/clears the uploaded file
    st.session_state.df = None
    st.session_state.original_df = None
    st.session_state.last_uploaded_file = None

tabs = st.tabs([
    "🔍 Schema & Inspection",
    "🧹 Clean & Transform",
    "📑 File Merger",
    "📊 Bar Chart Analysis",
])

# TAB 1: Inspection
with tabs[0]:
    st.subheader("Data Column Type Identifier")
    if st.session_state.df is not None:
        processor = DataProcessor(st.session_state.df)
        info_df = processor.identify_column_types()

        # Transpose so columns are along the top and metrics are on the left
        transposed_info = info_df.set_index("Column Name").T
        transposed_info.index.name = "Metric"

        st.dataframe(transposed_info, use_container_width=True)
        st.subheader("Data Preview")
        st.dataframe(st.session_state.df.head(10), use_container_width=True)
    else:
        st.info("Upload a file in the sidebar to inspect columns.")
        
# TAB 2: Cleaning (Deduplication & Dynamic Distinct Value Filtering)
with tabs[1]:
    st.subheader("File Processing & Cleaning")

    if "df" in st.session_state and st.session_state.df is not None:
        if "data_version" not in st.session_state:
            st.session_state.data_version = 0

        # =========================================================
        # 1. PREVIEW 1: BEFORE APPLYING (Original Uploaded File)
        # =========================================================
        top_header_col, top_reset_col = st.columns([4, 1])
        with top_header_col:
            orig_df = st.session_state.original_df
            st.write(f"##### 📊 Preview 1: Original Uploaded Data ({len(orig_df)} rows × {len(orig_df.columns)} cols)")
        with top_reset_col:
            if st.button("🔄 Reset All Changes"):
                st.session_state.df = st.session_state.original_df.copy()
                st.session_state.last_action = "Reset back to original upload."
                st.session_state.data_version += 1
                st.rerun()

        st.dataframe(orig_df.head(50), use_container_width=True)
        st.caption(f"Showing first {min(50, len(orig_df))} of {len(orig_df)} rows.")

        st.divider()

        # =========================================================
        # 2. CONTROLS: DEDUPLICATION & DYNAMIC VALUE FILTERING
        # =========================================================
        current_working_df = st.session_state.df

        # -----------------------------
        # Deduplication Section
        # -----------------------------
        st.write("##### 1. Deduplication")
        col_dedup1, col_dedup2 = st.columns([3, 1])
        with col_dedup1:
            cols_to_check = st.multiselect(
                "Columns to check for duplicates (leave blank for all)",
                current_working_df.columns,
                key=f"dedup_cols_{st.session_state.data_version}"
            )
        with col_dedup2:
            keep_strategy = st.radio("Keep record:", ["first", "last"], horizontal=True, key="keep_rad")

        subset_param = cols_to_check if cols_to_check else None
        dup_mask = current_working_df.duplicated(subset=subset_param, keep=False)
        dup_rows = current_working_df[dup_mask]
        dup_count = len(dup_rows)

        if dup_count > 0:
            st.warning(f"⚠️ Found **{dup_count}** duplicate records.")
            with st.expander("🔍 Preview Duplicate Records Only", expanded=False):
                st.dataframe(
                    dup_rows.sort_values(by=subset_param if subset_param else list(current_working_df.columns)),
                    use_container_width=True
                )
        else:
            st.success("✅ No duplicate records detected.")

        if st.button("Run Deduplication", disabled=(dup_count == 0)):
            cleaned = current_working_df.drop_duplicates(subset=subset_param, keep=keep_strategy)
            removed_count = len(current_working_df) - len(cleaned)
            st.session_state.df = cleaned
            st.session_state.last_action = f"Deduplication removed {removed_count} duplicate rows."
            st.session_state.data_version += 1
            st.rerun()

        st.divider()

        # ---------------------------------------------------------
        # Dynamic Multi-Column Distinct Values Filter Section
        # ---------------------------------------------------------
        st.write("##### 2. Dynamic Value Filtering")
        st.caption("Select columns to filter, then choose specific distinct values from each.")

        # Step A: Select which columns the user wants to filter by
        selected_filter_columns = st.multiselect(
            "Select columns to add filters for:",
            options=list(current_working_df.columns),
            key=f"active_filter_cols_{st.session_state.data_version}"
        )

        filter_selections = {}
        if selected_filter_columns:
            # Dynamically generate input columns (up to 3 dropdowns per row)
            num_cols = min(3, len(selected_filter_columns))
            ui_cols = st.columns(num_cols)

            for idx, col_name in enumerate(selected_filter_columns):
                # Extract sorted distinct non-null values
                distinct_values = sorted(current_working_df[col_name].dropna().unique().tolist())

                with ui_cols[idx % num_cols]:
                    chosen_values = st.multiselect(
                        f"Values for '{col_name}':",
                        options=distinct_values,
                        key=f"val_filter_{col_name}_{st.session_state.data_version}",
                        placeholder="Select values to keep..."
                    )
                    if chosen_values:
                        filter_selections[col_name] = chosen_values

        # Build dynamic boolean mask across all selected dropdowns
        active_filtered_df = current_working_df.copy()
        if filter_selections:
            mask = pd.Series(True, index=current_working_df.index)
            for col_name, values in filter_selections.items():
                mask = mask & current_working_df[col_name].isin(values)
            active_filtered_df = current_working_df[mask]

            st.info(f"🔎 Match found: **{len(active_filtered_df)}** out of **{len(current_working_df)}** rows.")

            # Live preview before applying
            with st.expander("👁️ Preview Filtered Rows Before Applying", expanded=True):
                st.dataframe(active_filtered_df.head(50), use_container_width=True)

            if st.button("✅ Confirm & Apply Filter"):
                st.session_state.df = active_filtered_df
                st.session_state.last_action = f"Filtered across {len(filter_selections)} column(s): retained {len(active_filtered_df)} rows."
                st.session_state.data_version += 1
                st.rerun()

        st.divider()

        # =========================================================
        # 3. PREVIEW 2: AFTER APPLYING (Updated Working Dataset)
        # =========================================================
        active_df = st.session_state.df

        st.write(f"##### 📊 Preview 2: After Applying ({len(active_df)} rows × {len(active_df.columns)} cols)")
        if st.session_state.get("last_action"):
            st.success(f"⚡ **Status:** {st.session_state.last_action}")

        st.dataframe(
            active_df.head(100),
            use_container_width=True,
            key=f"preview_after_table_{st.session_state.data_version}"
        )
        st.caption(f"Showing first {min(100, len(active_df))} of {len(active_df)} rows.")

        # =========================================================
        # 4. DOWNLOAD PROCESSED DATA (CSV & EXCEL)
        # =========================================================
        st.write("##### 📥 Download Processed Data")
        dl_col1, dl_col2 = st.columns(2)

        # 1. Download as CSV
        with dl_col1:
            csv_buf = active_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Download as CSV",
                data=csv_buf,
                file_name="oneprocess_processed.csv",
                mime="text/csv",
                use_container_width=True
            )

        # 2. Download as Excel (.xlsx)
        with dl_col2:
            import io
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                active_df.to_excel(writer, index=False, sheet_name="ProcessedData")
            excel_buf.seek(0)

            st.download_button(
                label="📊 Download as Excel (.xlsx)",
                data=excel_buf.getvalue(),
                file_name="oneprocess_processed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    else:
        st.info("Upload a dataset in the sidebar first.")

# TAB 3: File Merger
with tabs[2]:
    st.subheader("File Merging Tool")
    st.write("Merge two files that share identical or overlapping column names.")
    file1 = st.file_uploader("Upload First File", type=["csv", "xlsx"], key="m_file1")
    file2 = st.file_uploader("Upload Second File", type=["csv", "xlsx"], key="m_file2")
    merge_mode = st.radio("Merge Mode", ["concat (Vertical Stack)", "inner (Common Columns Only)"], horizontal=True)

    if file1 and file2 and st.button("Merge Files"):
        mode = "concat" if "concat" in merge_mode else "inner"
        merged_df = DataProcessor.merge_files(file1, file2, how=mode)
        st.success(f"Successfully merged! Total rows: {len(merged_df)}")
        st.dataframe(merged_df.head(10), use_container_width=True)
        st.download_button(
            label="📥 Download Merged File",
            data=merged_df.to_csv(index=False).encode('utf-8'),
            file_name="merged_output.csv",
            mime="text/csv"
        )

# TAB 4: Bar Graphs with Notes
with tabs[3]:
    st.subheader("Bar Graph Analysis")

    if st.session_state.get("df") is not None:
        # Check if the active dataset was updated in Tab 2
        current_data_version = st.session_state.get("data_version", 0)
        if st.session_state.get("last_seen_data_version") != current_data_version:
            st.session_state.chart_fig = None
            st.session_state.chart_notes_saved = ""
            st.session_state.last_seen_data_version = current_data_version

        # Initialize chart state trackers
        if "chart_fig" not in st.session_state:
            st.session_state.chart_fig = None
        if "chart_notes_saved" not in st.session_state:
            st.session_state.chart_notes_saved = ""
        if "chart_version" not in st.session_state:
            st.session_state.chart_version = 0

        # Display reset notification if user recently reset the chart
        if st.session_state.get("show_filter_reset_msg"):
            st.warning("ℹ️ Chart reset! If you want to analyze the full original dataset, please reset the filtering in the **Clean & Transform** tab.")

        df = st.session_state.df

        # Controls & Dropdowns
        c1, c2, c3 = st.columns(3)
        with c1:
            x_axis = st.selectbox(
                "Category (X-axis)", 
                df.columns, 
                key=f"chart_x_{st.session_state.chart_version}"
            )
        with c2:
            num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            y_axis = st.selectbox(
                "Metric (Y-axis)", 
                num_cols if num_cols else df.columns, 
                key=f"chart_y_{st.session_state.chart_version}"
            )
        with c3:
            agg = st.selectbox(
                "Aggregation", 
                ["sum", "mean", "count"], 
                key=f"chart_agg_{st.session_state.chart_version}"
            )

        chart_notes = st.text_area(
            "Analysis / Observation Notes", 
            value=st.session_state.chart_notes_saved,
            placeholder="Type key insights about this distribution...",
            key=f"chart_notes_input_{st.session_state.chart_version}"
        )

        # Action Buttons: Generate & Reset
        btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 5])

        with btn_col1:
            if st.button("📊 Generate Chart", type="primary", use_container_width=True):
                # Clear the reminder message on new generation
                st.session_state.show_filter_reset_msg = False
                
                fig = GraphAnalyzer.create_bar_chart(
                    df, 
                    x_col=x_axis, 
                    y_col=y_axis, 
                    aggregation=agg, 
                    title=f"{agg.capitalize()} of {y_axis} by {x_axis}"
                )
                st.session_state.chart_fig = fig
                st.session_state.chart_notes_saved = chart_notes
                st.rerun()

        with btn_col2:
            if st.button("🔄 Reset Chart", use_container_width=True):
                st.session_state.chart_fig = None
                st.session_state.chart_notes_saved = ""
                st.session_state.chart_version += 1
                # Trigger the reminder message
                st.session_state.show_filter_reset_msg = True
                st.rerun()

        # Display chart and notes if generated
        if st.session_state.chart_fig is not None:
            st.divider()
            st.plotly_chart(st.session_state.chart_fig, use_container_width=True)
            if st.session_state.chart_notes_saved:
                st.info(f"**Section Notes:** {st.session_state.chart_notes_saved}")

    else:
        st.info("Upload data in the sidebar to generate charts.")