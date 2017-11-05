FROM centos:7

RUN yum -y update && \
    yum -y install epel-release && \
    yum -y install python-pip

# Add your pip packages
RUN pip install rq && \
    pip install azure-keyvault

WORKDIR /usr/src/app

CMD ["python"]
