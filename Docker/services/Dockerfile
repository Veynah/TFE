FROM python:3.12-slim-bookworm AS builder

RUN apt-get update && apt-get install -y git gcc
RUN mkdir -p ~/.ssh && chmod 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
WORKDIR /root/

RUN --mount=type=ssh git clone git@github.com:Veynah/odoo_template.git --branch=main --depth=1 project_addons && rm -fr project_addons/.git
WORKDIR /root/project_addons
RUN if [ -f build/prehook-builder.sh ]; then sh build/prehook-builder.sh; fi
RUN mkdir -p /root/python && if [ -f requirements.txt ]; then pip wheel -r requirements.txt -w /root/python ; fi

FROM 127.0.0.1:5000/odoo:18.0_community AS runner
COPY --from=builder /root/project_addons /opt/odoo/project_addons
COPY --from=builder /root/python /root/python

USER root
# RUN apt-get update && apt-get install -y libcairo2 libcairo2-dev && rm -rf /var/lib/apt/lists/*
RUN if [ -f /opt/odoo/project_addons/build/prehook-runner.sh ]; then sh /opt/odoo/project_addons/build/prehook-runner.sh; fi
RUN if [ -n "$(ls -A /root/python)" ]; then python -m pip install /root/python/* ; fi && rm -fr /root/python
# RUN mkdir -p /var/lib/odoo && chown -R odoo:odoo /var/lib/odoo

# USER odoo
ENV ADDONS_PATH="$ADDONS_PATH,/opt/odoo/project_addons"
