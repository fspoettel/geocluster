from sklearn.cluster import DBSCAN, OPTICS
import numpy as np


def km_to_radians(km):
    """Convert kilometer distance to radians."""
    return km / 6378.1


def to_cluster_dict(df, clustering):
    """
    Creates a dict <cluster_id, list[dict]>.
    Each key corresponds to a cluster_id and holds a list of matching location data as dict.
    """
    clusters_by_id = {}

    print(clustering.labels_)

    for idx, cluster_id in enumerate(clustering.labels_):
        # ignore "noise" locations that don't belong to any cluster.
        if cluster_id > -1:
            data = df.iloc[idx]
            clusters_by_id.setdefault(cluster_id, []).append(data.to_dict())

    return clusters_by_id


def is_valid_lat(val: str) -> bool:
    """Given a string, check if it corresponds to a valid decimal latitude value"""
    try:
        val = float(val)
        return val >= -90 and val <= 90
    except:
        return False


def is_valid_lon(val: str) -> bool:
    """Given a string, check if it corresponds to a valid decimal longitude value"""
    try:
        val = float(val)
        return val >= -180 and val <= 180
    except:
        return False


def cluster_locations(df, algorithm, radius_km, min_cluster_size):
    """
    Clusters a location dataframe into clusters.
    A cluster is constructed when there are more than `min_cluster_size locations
    within `radius_km` of each other.
    Outputs a dict grouping locations by `cluster_id`.
    """
    valid_index = df.lat.astype(str).apply(is_valid_lat) & df.lon.astype(str).apply(
        is_valid_lon
    )
    if len(df_invalid := df[~valid_index]):
        print(f"Found {len(df_invalid)} invalid coordinate pairs, ignoring:")
        print(df_invalid[["lat", "lon"]])
    df = df[valid_index]

    coordinates = df[["lat", "lon"]]
    radius_radians = km_to_radians(radius_km)

    if algorithm == "dbscan":
        clustering = DBSCAN(
            eps=radius_radians,
            min_samples=min_cluster_size,
            metric="haversine",
            n_jobs=-1,
        )
    else:
        clustering = OPTICS(
            max_eps=radius_radians,
            min_samples=min_cluster_size,
            metric="haversine",
            n_jobs=-1,
        )

    X = np.radians(np.array(coordinates).astype(float))
    return to_cluster_dict(df, clustering.fit(X))
