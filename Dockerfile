FROM python
WORKDIR /mattyermost
COPY . /mattyermost
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app.py"]
