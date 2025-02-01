FROM postgres:15

# Custom PostgreSQL configuration can be added here if needed
# COPY postgresql.conf /etc/postgresql/postgresql.conf

# Add any additional setup steps here if needed
# For example, installing extensions or tools

# Health check to verify database is ready
HEALTHCHECK --interval=30s --timeout=3s \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} || exit 1