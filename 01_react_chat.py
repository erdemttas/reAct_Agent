from langchain.agents import create_react_agent, AgentExecutor, load_tools
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
import streamlit as st
import custom_tools
import os
from dotenv import load_dotenv

load_dotenv()

my_key_google = os.getenv("my_key_gemini")
my_key_openai = os.getenv("my_key_openai")
my_key_anthropic = os.getenv("my_key_anthropic")
os.environ["TAVILY_API_KEY"] = os.getenv("tavily_apikey")

llm_gemini = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=my_key_google)
llm_openai = ChatOpenAI(api_key=my_key_openai, model="gpt-3.5-turbo")
llm_claude = ChatAnthropic(model="claude-2.1", anthropic_api_key=my_key_anthropic)

agent_prompt = hub.pull("hwchase17/react")

def configure_agent(selected_llm, selected_search_engine, selected_image_generator=""):
    if selected_llm == "GPT":
        llm = llm_openai
    elif selected_llm == "Gemini Pro":
        llm = llm_gemini
    elif selected_llm == "Claude 2.1":
        llm = llm_claude

    web_scraping_tool = custom_tools.get_web_tool()

    if selected_search_engine == "DuckDuckGo":
        tools = load_tools(["ddg-search"])
        tools.extend([web_scraping_tool])
    elif selected_search_engine == "Tavily":
        tools = [TavilySearchResults(max_results=1), web_scraping_tool]


    agent = create_react_agent(llm=llm, tools=tools, prompt=agent_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)

    return agent_executor
#--------------------------------------------------------------------------------------


st.set_page_config(page_title="ReAct Ajan ile Sohbet Etkileşimi")
st.image(image="angara.png")
st.title("React Ajan ile Sohbet Etkileşimi")
st.divider()

st.sidebar.header("Ajan Konfigürasyonu")
st.sidebar.divider()
selected_llm = st.sidebar.radio(label="Dil Modeli Seçiniz", options=["GPT", "Gemini Pro", "Claude 2.1"])
st.sidebar.divider()
selected_search_engine = st.sidebar.radio(label="Arama Motorunu Seçiniz", options=["DuckDuckGo", "Tavily"], index=1)
st.sidebar.divider()
selected_image_generator = st.sidebar.radio(label="Resim üretim Modelini Seçiniz", options=["Stable Diffusion XL", "DALL-E 3"])
st.sidebar.divider()
selected_web_scraper = st.sidebar.radio(label="Web Kazıma Aracı Seçiniz", options=["BeautifulSoup"])
st.sidebar.divider()
turkish_sensitivity = st.sidebar.checkbox(label="Türkçe Yanıta Zorla", value=True)
st.sidebar.divider()
reset_chat_btn = st.sidebar.button(label="Sohbet Geçmişini Sıfırla")


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input(placeholder="Mesajınızı Yazınız: "):
    st.chat_message("user").write(prompt)

    if turkish_sensitivity:
        st.session_state.messages.append({"role":"user", "content": prompt + "Bu soruyu Türkçe yanıtla"})
    else:
        st.session_state.messages.append({"role":"user", "content": prompt})


    with st.chat_message("assistant"):
        st.info("🧠 Düşünce Zinciri İşletiliyor...")

        st_callback = StreamlitCallbackHandler(st.container())
        executor = configure_agent(selected_llm=selected_llm, selected_search_engine=selected_search_engine)
        AI_Response = executor.invoke(
            {"input":st.session_state.messages}, {"callbacks":[st_callback]},
            handle_parsing_errors=True
        )

        st.markdown(AI_Response["output"], unsafe_allow_html=True)
        st.session_state.messages.append({"role":"assistant", "content":AI_Response["output"]})


if reset_chat_btn:
    st.session_state.messages = []
    st.toast("Sohbet Geçmişi Sıfırlandı!")










