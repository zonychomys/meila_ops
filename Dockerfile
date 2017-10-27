FROM centos:7
MAINTAINER leezhao<leezhao@meilapp.com>
COPY . /opt/meila_ops
WORKDIR /opt/meila_ops
RUN set -x \
    && yum -y install epel-release \
    && yum clean all \
    && yum makecache fast \
    && yum -y install \
        gcc \
        gcc-c++ \
        initscripts \
        libffi-devel \
        mariadb-devel \
        openssh-server \
        python-pip \
        python-devel \
        sshpass \
    && sed -i 's/#Port 22/Port 2227/g' /etc/ssh/sshd_config \
    && /usr/sbin/sshd-keygen \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && ln -sf `pwd`/utils/docker-entrypoint.sh /usr/local/bin/ \
    && ln -sf `pwd`/meila_ops/settings.template.py meila_ops/settings.py \
    && pip install -r requirement.txt \
        --index-url http://pypi.doubanio.com/simple/ \
        --trusted-host pypi.doubanio.com
ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 2226
EXPOSE 2227
CMD ["python", "manage.py", "runserver", "0.0.0.0:2226"]
