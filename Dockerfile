# FROM --platform=$BUILDPLATFORM ubuntu:20.04 AS base
FROM  ubuntu:20.04 AS base
RUN apt-get update
# Install system dependencies
RUN   apt-get install -y \
    gcc \
    libffi-dev \
    python3-dev \
    python3-pip \

    libzbar0 \     
    curl \
    gnupg \
    unzip \
    # libzbar-dev \  
    # xvfb \
    chromium-browser \  
    chromium-chromedriver \ 
    wget \ 
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*



ENV PATH="/usr/lib/chromium-browser/:${PATH}"

# ENV CHROMEDRIVER_VERSION 2.19
# ENV CHROMEDRIVER_DIR /chromedriver
# RUN mkdir $CHROMEDRIVER_DIR
# RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
# RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# ENV PATH $CHROMEDRIVER_DIR:$PATH

WORKDIR /app

# Copy Python dependencies file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . /app/

# Set the default command to execute
ENTRYPOINT ["python3"]
CMD ["app.py"]