mkdir -p ~/.streamlit
echo "\
[server]\n\
enableCORS = false\n\
headless = true\n\
port = $PORT\n\
\n\
[theme]\n\
primaryColor = '#88D600'\n\
backgroundColor = '#FFFFFF'\n\
secondaryBackgroundColor = '#F2F2F2'\n\
textColor = '#000000'\n\
base = 'light'\n\
" > ~/.streamlit/config.toml