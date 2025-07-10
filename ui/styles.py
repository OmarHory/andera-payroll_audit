STREAMLIT_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    .stApp, .stApp > div, .main, .block-container {
        background: transparent !important;
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    
    .stApp {
        background: #667eea !important;
        background: linear-gradient(-45deg, #667eea, #764ba2, #667eea, #f093fb, #764ba2) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 8s ease infinite !important;
        min-height: 100vh !important;
        position: relative !important;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(-45deg, 
            #667eea, 
            #764ba2, 
            #667eea, 
            #f093fb, 
            #764ba2);
        background-size: 400% 400%;
        animation: gradientBG 8s ease infinite;
        z-index: -2;
        pointer-events: none;
    }
    
    body {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 8s ease infinite !important;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 50%; }
        50% { background-position: 0% 100%; }
        75% { background-position: 100% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    .main > div > div {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        z-index: 1;
    }
    
    .stApp > .main {
        background: transparent !important;
    }
    
    .stApp > .main > div {
        background: transparent !important;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
        animation: particles 20s linear infinite;
        z-index: -1;
        pointer-events: none;
    }
    
    @keyframes particles {
        0% { transform: translateY(0px) rotate(0deg); }
        100% { transform: translateY(-100px) rotate(360deg); }
    }
    
    .header-section {
        background: linear-gradient(135deg, rgba(74, 85, 104, 0.95), rgba(102, 126, 234, 0.95));
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 3rem 2rem;
        margin: 2rem 0;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 4s infinite;
    }
    
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #4a5568 0%, #667eea 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(74, 85, 104, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .upload-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        100% { transform: translateX(100%); }
    }
    
    .upload-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .task-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .task-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite 1s;
    }
    
    .task-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .execution-section {
        background: linear-gradient(135deg, #38b2ac 0%, #4299e1 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(56, 178, 172, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .execution-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite 2s;
    }
    
    .execution-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .results-section {
        background: linear-gradient(135deg, #ed8936 0%, #f6ad55 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(237, 137, 54, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .results-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite 1.5s;
    }
    
    .results-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4a5568, #667eea);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 25px rgba(74, 85, 104, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 20px 40px rgba(74, 85, 104, 0.5);
        background: linear-gradient(135deg, #667eea, #38b2ac);
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(1.02);
    }
    
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.4);
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.6);
        transform: scale(1.02);
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.7);
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #4a5568, #667eea, #38b2ac, #4299e1);
        background-size: 200% 100%;
        animation: progressShine 2s linear infinite;
    }
    
    @keyframes progressShine {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #38b2ac, #4299e1);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
    }
    
    .stError {
        background: linear-gradient(135deg, #e53e3e, #fc8181);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ed8936, #f6ad55);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
    }
    
    .floating {
        animation: floating 6s ease-in-out infinite;
    }
    
    @keyframes floating {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
</style>
""" 