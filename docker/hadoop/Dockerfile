# =============================================================================
# Hadoop image — extends apache/hadoop:3.4.1 with Python and project scripts.
# =============================================================================
FROM apache/hadoop:3.4.1

USER root

# CentOS 7 base — repos moved to vault after EOL.
RUN sed -i 's|^mirrorlist=|#mirrorlist=|g; s|^#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo \
    && yum install -y python3 \
    && yum clean all \
    && ln -sf /usr/bin/python3 /usr/bin/python

COPY src/hadoop /opt/mapreduce
COPY docker/hadoop/scripts /opt/scripts

RUN chmod +x /opt/mapreduce/*.py /opt/scripts/*.sh

USER hadoop
