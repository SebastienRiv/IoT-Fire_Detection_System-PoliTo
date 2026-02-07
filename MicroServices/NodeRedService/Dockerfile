FROM nodered/node-red:latest

USER root
RUN npm install --no-audit --no-update-notifier --no-fund --only=production \
    node-red-dashboard \
    node-red-contrib-python3-function
USER node-red

WORKDIR /data
COPY --chown=node-red:node-red ./project/NodeRed_ProjectV4.json /data/flows.json

EXPOSE 1880

ENTRYPOINT []
CMD ["node-red"]