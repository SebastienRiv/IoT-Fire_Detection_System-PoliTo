FROM eclipse-mosquitto:latest

# Copier le fichier de configuration
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

# Exposer le port MQTT
EXPOSE 1883

# Commande par défaut
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]