import polars as pl


def build_features(lf: pl.LazyFrame) -> pl.LazyFrame:
    return (
        lf.with_columns(
            [
                pl.col("timestamp").dt.hour().alias("hour"),
                (pl.col("timestamp").dt.weekday().is_in([6, 7])).alias("is_weekend"),
                pl.col("is_holiday").cast(pl.Int8),
            ]
        )
        .with_columns(
            [
                (2 * pl.lit(3.141592653589793) * pl.col("hour") / 24)
                .sin()
                .alias("hour_sin"),
                (2 * pl.lit(3.141592653589793) * pl.col("hour") / 24)
                .cos()
                .alias("hour_cos"),
            ]
        )
        .with_columns(
            pl.col("throughput")
            .rolling_mean(window_size=7)
            .over("station_id")
            .alias("throughput_7d_avg")
        )
    )
