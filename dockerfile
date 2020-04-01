FROM python:3.7

COPY . /blockchain

WORKDIR /blockchain

RUN pip install ./pymerkletools

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

EXPOSE 5000

CMD ["app.py"]
