CREATE TABLE dim_date (
                          date_id         INT PRIMARY KEY,
                          full_date       DATE NOT NULL UNIQUE,
                          year            SMALLINT NOT NULL,
                          quarter         SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
                          month           SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
                          month_name      VARCHAR(20) NOT NULL,
                          day             SMALLINT NOT NULL CHECK (day BETWEEN 1 AND 31),
                          day_of_week     SMALLINT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
                          day_name        VARCHAR(20) NOT NULL,
                          is_weekend      BOOLEAN NOT NULL
);

CREATE TABLE dim_time (
                          hour            SMALLINT PRIMARY KEY CHECK (hour BETWEEN 0 AND 23),
                          period          VARCHAR(20) NOT NULL
);

INSERT INTO dim_time (hour, period)
VALUES
    (0, 'Nuit'),
    (1, 'Nuit'),
    (2, 'Nuit'),
    (3, 'Nuit'),
    (4, 'Nuit'),
    (5, 'Matin'),
    (6, 'Matin'),
    (7, 'Matin'),
    (8, 'Matin'),
    (9, 'Matin'),
    (10, 'Matin'),
    (11, 'Matin'),
    (12, 'Après-midi'),
    (13, 'Après-midi'),
    (14, 'Après-midi'),
    (15, 'Après-midi'),
    (16, 'Après-midi'),
    (17, 'Soir'),
    (18, 'Soir'),
    (19, 'Soir'),
    (20, 'Soir'),
    (21, 'Nuit'),
    (22, 'Nuit'),
    (23, 'Nuit')
    ON CONFLICT (hour) DO NOTHING;

CREATE TABLE dim_location (
                              location_id     SERIAL PRIMARY KEY,
                              city            VARCHAR(100) NOT NULL,
                              country         VARCHAR(100) NOT NULL,
                              latitude        DOUBLE PRECISION,
                              longitude       DOUBLE PRECISION,
                              UNIQUE (city, country)
);

CREATE TABLE dim_aqi_category (
                                  aqi             SMALLINT PRIMARY KEY,
                                  label           VARCHAR(30) NOT NULL,
                                  description     VARCHAR(150) NOT NULL
);

INSERT INTO dim_aqi_category (
    aqi,
    label,
    description
)
VALUES
    (1, 'Bon', 'Qualité de l’air satisfaisante'),
    (2, 'Correct', 'Qualité de l’air acceptable'),
    (3, 'Modéré', 'Risque pour les personnes sensibles'),
    (4, 'Mauvais', 'Effets possibles sur la santé'),
    (5, 'Très mauvais', 'Alerte sanitaire')
    ON CONFLICT (aqi) DO NOTHING;


CREATE TABLE fact_air_quality_hourly (
                                         extraction_id           UUID NOT NULL,
                                         extraction_timestamp    TIMESTAMPTZ NOT NULL,
                                         date_id                 INT NOT NULL,
                                         hour                    SMALLINT NOT NULL,
    location_id             INT NOT NULL,
    measurement_timestamp   TIMESTAMPTZ NOT NULL,
    aqi                     SMALLINT,
    co                      DOUBLE PRECISION,
    no                      DOUBLE PRECISION,
    no2                     DOUBLE PRECISION,
    o3                      DOUBLE PRECISION,
    so2                     DOUBLE PRECISION,
    pm2_5                   DOUBLE PRECISION,
    pm10                    DOUBLE PRECISION,
    nh3                     DOUBLE PRECISION,


    PRIMARY KEY (
        location_id,
        measurement_timestamp
    ),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    FOREIGN KEY (hour)
        REFERENCES dim_time(hour),

    FOREIGN KEY (location_id)
        REFERENCES dim_location(location_id),

    FOREIGN KEY (aqi)
        REFERENCES dim_aqi_category(aqi),

    CONSTRAINT chk_aqi_range
        CHECK (
            aqi IS NULL
            OR aqi BETWEEN 1 AND 5
        )

);

CREATE INDEX idx_fact_air_quality_date
    ON fact_air_quality_hourly(date_id);

CREATE INDEX idx_fact_air_quality_hour
    ON fact_air_quality_hourly(hour);

CREATE INDEX idx_fact_air_quality_location
    ON fact_air_quality_hourly(location_id);

CREATE INDEX idx_fact_air_quality_measurement
    ON fact_air_quality_hourly(measurement_timestamp);

CREATE INDEX idx_fact_air_quality_extraction
    ON fact_air_quality_hourly(extraction_id);