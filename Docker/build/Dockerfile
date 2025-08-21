ARG PYTHON_VERSION=3.12-slim-bookworm
ARG ODOO_VERSION=18.0
ARG ODOO_THEME_VERSION=18.0

FROM python:$PYTHON_VERSION AS builder

ARG ODOO_VERSION=$ODOO_VERSION
ARG ODOO_THEME_VERSION=$ODOO_THEME_VERSION

RUN apt-get update && apt-get install -y git postgresql wget libsasl2-dev python-dev-is-python3 libldap2-dev libssl-dev libpq-dev gcc
RUN mkdir -p ~/.ssh && chmod 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
WORKDIR /root

RUN --mount=type=ssh git init odoo && git --git-dir=./odoo/.git remote add origin git@github.com:odoo/odoo.git && git --git-dir=./odoo/.git fetch --depth 1 origin $ODOO_VERSION && git --git-dir=./odoo/.git checkout $ODOO_VERSION && echo "$(git --git-dir=./odoo/.git rev-parse HEAD)" >> ./odoo/addons/commit.txt && rm -fr odoo/.git

RUN --mount=type=ssh git clone git@github.com:odoo/design-themes.git --branch=$ODOO_THEME_VERSION --depth=1 && echo "$(git --git-dir=./design-themes/.git rev-parse HEAD)" >> ./design-themes/commit.txt && rm -fr design-themes/.git
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb -O /root/wkhtmltox.deb
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb -O /root/libssl.deb
RUN wget http://mirrors.kernel.org/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_2.1.2-0ubuntu1_amd64.deb -O /root/libjpeg-turbo8.deb
RUN mkdir -p /root/python && python -m pip wheel -r odoo/requirements.txt -w /root/python --prefer-binary

FROM python:$PYTHON_VERSION AS runner

ARG ODOO_VERSION=$ODOO_VERSION

COPY --from=builder /root /root

RUN apt-get update && apt-get install -y libpq-dev node-less xmlsec1 libfreetype6-dev fontconfig unixodbc fonts-font-awesome libxext6 libxrender1 libjpeg62-turbo xfonts-75dpi xfonts-base \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get install -y --no-install-recommends /root/libssl.deb && rm -fr /root/libssl.deb
RUN apt-get install -y --no-install-recommends /root/libjpeg-turbo8.deb && rm -fr /root/libjpeg-turbo8.deb
RUN apt-get install -y --no-install-recommends /root/wkhtmltox.deb && rm -rf /root/wkhtmltox.deb
RUN useradd --no-create-home --uid 1001 odoo
RUN mkdir -p /var/odoo/sessions /var/odoo/filestore /var/odoo/addons && chown -R odoo:odoo /var/odoo && mkdir -p /var/lib/odoo && chown -R odoo:odoo /var/lib/odoo
RUN python -m pip install /root/python/* && rm -fr /root/python && mv /root/odoo /opt && mv /root/design-themes /opt/odoo/design-themes && chown -R odoo:odoo /opt/odoo

USER odoo
ENV DB_HOST=postgres
ENV DB_USER=odoo
ENV DB_PASSWORD=odoo
ENV DB_NAME=odoo
ENV ADDONS_PATH=/opt/odoo/odoo/addons,/opt/odoo/addons,/opt/odoo/design-themes
ENV FILESTORE_PATH=/var/odoo
ENV WORKERS=2
ENV LIMIT_TIME_CPU=600
ENV LIMIT_TIME_REAL=1200

WORKDIR /opt/odoo
RUN echo '/opt/odoo/odoo-bin --without-demo=all --unaccent --addons-path=$ADDONS_PATH -D $FILESTORE_PATH --db_host=$DB_HOST --db_password=$DB_PASSWORD --db_user=$DB_USER --proxy-mode --workers=$WORKERS --no-database-list --limit-time-cpu=$LIMIT_TIME_CPU --limit-time-real=$LIMIT_TIME_REAL "$@"' > /opt/odoo/launcher.sh && chmod +x /opt/odoo/launcher.sh
CMD ["sh", "-c", "sh /opt/odoo/launcher.sh -d ${DB_NAME}"]

