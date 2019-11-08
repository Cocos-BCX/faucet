FROM registry-vpc.cn-beijing.aliyuncs.com/ck_chain/faucet:base
MAINTAINER cocosbcx
COPY init.sh .
COPY faucet_server.py .
COPY config.py  .
EXPOSE 80
EXPOSE 443
CMD bash ./init.sh
