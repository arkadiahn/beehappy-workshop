# Grafana for the BeeHappy beehive dashboard.
#
# Everything is provisioned from files in this directory, so the dashboard and
# its datasource live in git and survive a rebuild. Nothing has to be clicked
# together in the UI.
FROM grafana/grafana:11.6.0

# Datasource + dashboard provider definitions.
COPY provisioning/ /etc/grafana/provisioning/

# The dashboard JSON the provider above loads.
COPY dashboards/ /var/lib/grafana/dashboards/

EXPOSE 3000

LABEL org.opencontainers.image.title="beehappy-grafana"
