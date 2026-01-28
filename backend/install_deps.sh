echo "Installing all dependencies..."


pip install fastapi==0.104.1 \
            uvicorn==0.24.0 \
            sqlalchemy==2.0.23 \
            pydantic==2.5.0 \
            python-multipart==0.0.6 \
            pandas==2.1.4 \
            numpy==1.26.4 \
            aiofiles==23.2.1


pip install "python-jose[cryptography]==3.3.0"
pip install "passlib[bcrypt]==1.7.4"


pip install scikit-learn==1.3.2


pip install speechrecognition==3.10.0 \
            gtts==2.4.0 \
            pydub==0.25.1

echo "Installation complete!"