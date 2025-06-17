import bcrypt
import os
import time
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client import OAuthError
import streamlit as st

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "chave_padrao_apenas_para_desenvolvimento")
SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY", 1800))
LOGIN_ATTEMPTS_LIMIT = int(os.getenv("LOGIN_ATTEMPTS_LIMIT", 5))

USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"

USERS_FILE.parent.mkdir(exist_ok=True)

if not USERS_FILE.exists():
    with open(USERS_FILE, "w") as f:
        json.dump({"users": []}, f)

def load_users():
    """Carrega os usuários do arquivo JSON."""
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"users": []}

def save_users(users_data):
    """Salva os dados dos usuários no arquivo JSON."""
    with open(USERS_FILE, "w") as f:
        json.dump(users_data, f, indent=2)

def get_user_by_email(email):
    """Busca um usuário pelo e-mail."""
    users_data = load_users()
    for user in users_data.get("users", []):
        if user.get("email") == email:
            return user
    return None

def get_user_by_oauth(provider, provider_id):
    """Busca um usuário pelo ID do provedor OAuth."""
    users_data = load_users()
    for user in users_data.get("users", []):
        if user.get("oauth_provider") == provider and user.get("oauth_id") == provider_id:
            return user
    return None

def hash_password(password):
    """Gera o hash de uma senha usando bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_credentials(email, password, hashed_password):
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        # Hash inválido ou outro erro de verificação
        return False

def register_user(email, password=None, name=None, oauth_provider=None, oauth_id=None):
    """Registra um novo usuário ou atualiza um existente com dados OAuth."""
    users_data = load_users()
    
    # Verificar se o usuário já existe pelo e-mail
    existing_user = get_user_by_email(email)
    
    if existing_user:
        # Se o usuário já existe, atualiza com os dados OAuth se fornecidos
        if oauth_provider and oauth_id:
            existing_user["oauth_provider"] = oauth_provider
            existing_user["oauth_id"] = oauth_id
            save_users(users_data)
            return True
        return False # Usuário já existe e não é uma atualização OAuth
    
    # Criar novo usuário
    new_user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name if name else email.split('@')[0],
        "created_at": time.time()
    }
    
    if password:
        new_user["password"] = hash_password(password)
    
    if oauth_provider and oauth_id:
        new_user["oauth_provider"] = oauth_provider
        new_user["oauth_id"] = oauth_id
        
    users_data["users"].append(new_user)
    save_users(users_data)
    return True

def init_session():
    """Inicializa o estado da sessão do Streamlit."""
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
    print(f"[AUTH] init_session: st.session_state.auth = {st.session_state.auth}")

def login_user(user):
    """Define o usuário como autenticado na sessão."""
    st.session_state.auth = True
    st.session_state.user = user
    st.session_state.login_attempts = 0 
    st.session_state.last_activity = time.time()
    print(f"[AUTH] login_user: Usuário {user["email"]} logado. st.session_state.auth = {st.session_state.auth}")

def logout_user():
    """Limpa o estado da sessão para deslogar o usuário."""
    st.session_state.auth = False
    st.session_state.user = None
    st.session_state.login_attempts = 0
    st.session_state.last_activity = time.time()
    print(f"[AUTH] logout_user: st.session_state.auth = {st.session_state.auth}")

def authenticate_email_password(email, password):
    """Autentica um usuário com e-mail e senha."""
    user = get_user_by_email(email)
    if user and "password" in user:
        if verify_credentials(email, password, user["password"]):
            login_user(user)
            print(f"[AUTH] authenticate_email_password: Resultado da autenticação para {email}: True")
            return True
        else:
            increment_login_attempts()
            print(f"[AUTH] authenticate_email_password: Resultado da autenticação para {email}: False (senha inválida)")
            return False
    else:
        increment_login_attempts()
        print(f"[AUTH] authenticate_email_password: Resultado da autenticação para {email}: False (usuário não encontrado ou sem senha)")
        return False

def increment_login_attempts():
    """Incrementa o contador de tentativas de login."""
    st.session_state.login_attempts += 1

def is_login_attempts_exceeded():
    """Verifica se o limite de tentativas de login foi excedido."""
    return st.session_state.login_attempts >= LOGIN_ATTEMPTS_LIMIT

def check_session_expiry():
    """Verifica se a sessão expirou."""
    if st.session_state.auth and (time.time() - st.session_state.last_activity > SESSION_EXPIRY):
        logout_user()
        return True
    return False

def init_oauth():
    """Inicializa os clientes OAuth."""
    oauth = OAuth()

    return oauth