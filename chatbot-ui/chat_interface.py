import streamlit as st
import requests
import json

def get_stream_response(text, conversation_id):
    url = f"http://localhost:8000/v1/chat/stream"
    payload = json.dumps({
        "user_message": text,
        "conversation_id": conversation_id
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload, stream=True)
    if response.status_code != 200:
        raise TimeoutError(f"Request to bot fail: {response.text}")
    return response

def save_user_input_to_backend(user_input, conversation_id):
    try:
        url = f"http://localhost:8000/v1/save_user_input"
        payload = json.dumps({
            "user_input": user_input,
            "conversation_id": conversation_id
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error saving user input: {e}")
        return False

def create_new_conversation():
    try:
        url = f"http://localhost:8000/v1/conversations/new"
        response = requests.post(url)
        if response.status_code == 200:
            return json.loads(response.text)["conversation_id"]
    except Exception as e:
        st.error(f"Error creating conversation: {e}")
    return None

def get_conversations():
    try:
        url = f"http://localhost:8000/v1/conversations"
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
    except Exception as e:
        st.error(f"Error loading conversations: {e}")
    return []

def delete_conversation(conversation_id):
    try:
        url = f"http://localhost:8000/v1/conversations/{conversation_id}"
        response = requests.delete(url)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting conversation: {e}")
        return False

def cleanup_conversations():
    try:
        url = f"http://localhost:8000/v1/conversations/cleanup"
        response = requests.post(url)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error cleaning up conversations: {e}")
        return False

def load_conversation_messages(conversation_id):
    try:
        url = f"http://localhost:8000/v1/conversations/{conversation_id}"
        response = requests.get(url)
        if response.status_code == 200:
            messages = json.loads(response.text)["messages"]
            # Convert to streamlit format
            streamlit_messages = []
            for msg in messages:
                streamlit_messages.append({"role": "user", "content": msg["question"]})
                if msg["answer"]:
                    streamlit_messages.append({"role": "assistant", "content": msg["answer"]})
            return streamlit_messages
    except Exception as e:
        st.error(f"Error loading conversation: {e}")
    return []

st.title("💬 RAG Chatbot")

# Initialize session state
if "current_conversation_id" not in st.session_state:
    # Create new conversation on first load
    new_id = create_new_conversation()
    st.session_state.current_conversation_id = new_id

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("🛠 Conversations")
    
    # New conversation button
    if st.button("🆕 New Conversation", type="primary"):
        new_id = create_new_conversation()
        if new_id:
            st.session_state.current_conversation_id = new_id
            st.session_state.messages = []
            st.success("New conversation created!")
            st.rerun()
    
    st.divider()
    
    # Load conversations
    conversations = get_conversations()
    
    if conversations:
        st.subheader("📋 Your Conversations")
        for conv in conversations:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create button for each conversation
                if st.button(
                    f"💬 {conv['title']}", 
                    key=f"conv_{conv['id']}",
                    help=f"Messages: {conv['message_count']} | Created: {conv['created_at'][:10]}"
                ):
                    st.session_state.current_conversation_id = conv['id']
                    st.session_state.messages = load_conversation_messages(conv['id'])
                    st.rerun()
            
            with col2:
                # Delete button
                if st.button("🗑️", key=f"del_{conv['id']}", help="Delete conversation"):
                    if delete_conversation(conv['id']):
                        if st.session_state.current_conversation_id == conv['id']:
                            # If deleted current conversation, create new one
                            new_id = create_new_conversation()
                            st.session_state.current_conversation_id = new_id
                            st.session_state.messages = []
                        st.success("Conversation deleted!")
                        st.rerun()
    
    st.divider()
    
    # Display current conversation info
    # if st.session_state.current_conversation_id:
    #     st.info(f"Current: {st.session_state.current_conversation_id[:8]}...")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Save user input to backend
    save_user_input_to_backend(prompt, st.session_state.current_conversation_id)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Get streaming response
            stream_response = get_stream_response(prompt, st.session_state.current_conversation_id)
            
            for chunk in stream_response:
                full_response += chunk.decode("utf-8")
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            full_response = "Sorry, there was an error processing your request."
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Force refresh to update conversation title if this was the first message
    if len(st.session_state.messages) == 2:  # User message + Assistant response
        st.rerun()