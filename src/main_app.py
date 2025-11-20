import streamlit as st
import pandas as pd
import warnings
from core.data_processor import DataProcessor

warnings.filterwarnings('ignore')


def main():
    st.set_page_config(
        page_title="电商销售分析与策略优化系统",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    app = EcommerceSalesApp()
    app.run()


class EcommerceSalesApp:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.initialize_session_state()

    def initialize_session_state(self):
        default_states = {
            'raw_data': None,
            'task1_completed': False,
            'task2_completed': False,
            'task3_completed': False,
            'task4_completed': False,
            'current_file': None
        }

        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def show_project_overview(self):
        st.header("🎯 项目概览")
        st.markdown("""
        ### 电商销售分析与策略优化系统

        这是一个完整的电商销售分析平台，包含四个主要任务：

        - **📁 数据预处理**: 数据清洗、缺失值处理、标准化
        - **🔍 多维特征分析**: 交叉分析、客户画像、地理分布  
        - **📈 销售预测**: 时间序列预测、趋势分析
        - **💡 运营优化**: ABC分类、价格敏感度分析、策略推荐
        """)

        st.subheader("任务完成状态")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = "✅ 已完成" if st.session_state.task1_completed else "⏳ 待完成"
            st.metric("数据预处理", status)

        with col2:
            status = "✅ 已完成" if st.session_state.task2_completed else "⏳ 待完成"
            st.metric("多维分析", status)

        with col3:
            status = "✅ 已完成" if st.session_state.task3_completed else "⏳ 待完成"
            st.metric("销售预测", status)

        with col4:
            status = "✅ 已完成" if st.session_state.task4_completed else "⏳ 待完成"
            st.metric("运营优化", status)

    def run(self):
        st.sidebar.title("📊 导航菜单")
        page = st.sidebar.radio(
            "选择页面:",
            ["项目概览", "数据预处理", "多维分析", "销售预测", "运营优化", "系统状态"]
        )

        if page == "项目概览":
            self.show_project_overview()
        elif page == "数据预处理":
            st.header("📁 数据预处理")
            st.info("数据预处理功能开发中...")
        elif page == "多维分析":
            st.header("🔍 多维特征分析")
            st.info("多维分析功能开发中...")
        elif page == "销售预测":
            st.header("📈 销售预测")
            st.info("销售预测功能开发中...")
        elif page == "运营优化":
            st.header("💡 运营优化")
            st.info("运营优化功能开发中...")
        elif page == "系统状态":
            st.header("⚙️ 系统状态")
            st.info("系统状态页面开发中...")


if __name__ == "__main__":
    main()