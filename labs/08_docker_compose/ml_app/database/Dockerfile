FROM postgres:14.0

# Optional: Set environment variables for configuration
# ENV POSTGRES_USER user
# ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB sentiment_db  # Adjust if needed

EXPOSE 5432

CMD ["postgres", "-D", "/var/lib/postgresql/data"]
