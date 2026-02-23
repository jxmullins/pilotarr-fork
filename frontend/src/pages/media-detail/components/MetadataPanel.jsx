import React from "react";
import Icon from "../../../components/AppIcon";

const MetadataPanel = ({ media }) => {
  const jellyfinUrl =
    media?.jellyfinId && media?.serviceUrls?.jellyfin
      ? `${media.serviceUrls.jellyfin}/web/index.html#!/details?id=${media.jellyfinId}`
      : null;

  const sonarrUrl =
    media?.mediaType === "tv" && media?.serviceUrls?.sonarr ? media.serviceUrls.sonarr : null;

  const radarrUrl =
    media?.mediaType === "movie" && media?.serviceUrls?.radarr ? media.serviceUrls.radarr : null;

  const addedDate = media?.addedDate
    ? new Date(media.addedDate).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : null;

  return (
    <div className="bg-card border border-border rounded-lg p-6 space-y-6">
      <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
        <Icon name="Info" size={20} className="text-primary" />
        Details
      </h2>

      {/* Overview */}
      {media?.overview && (
        <div>
          <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-2">Overview</h3>
          <p className="text-foreground leading-relaxed">{media.overview}</p>
        </div>
      )}

      {/* Quick info row */}
      <div className="flex flex-wrap gap-3">
        {/* Rating */}
        {media?.rating && (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-warning/10 border border-warning/20 rounded-full text-sm text-warning font-medium">
            <Icon name="Star" size={13} />
            {media.rating}
          </span>
        )}

        {/* Monitoring status */}
        {media?.mediaType === "tv" && (
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${
              media.monitored
                ? "bg-success/10 border-success/20 text-success"
                : "bg-muted/60 border-border text-muted-foreground"
            }`}
          >
            <Icon name={media.monitored ? "Bell" : "BellOff"} size={13} />
            {media.monitored ? "Monitored" : "Unmonitored"}
          </span>
        )}

        {/* Added date */}
        {addedDate && (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-muted/50 border border-border rounded-full text-sm text-muted-foreground">
            <Icon name="CalendarPlus" size={13} />
            Added {addedDate}
          </span>
        )}
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Release Date */}
        {media?.releaseDate && (
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-1">
              Release Date
            </h3>
            <p className="text-foreground">{media.releaseDate}</p>
          </div>
        )}

        {/* Status */}
        {media?.status && (
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-1">Status</h3>
            <p className="text-foreground">{media.status}</p>
          </div>
        )}

        {/* Network/Studio */}
        {media?.network && (
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-1">
              {media.mediaType === "tv" ? "Network" : "Studio"}
            </h3>
            <p className="text-foreground">{media.network}</p>
          </div>
        )}

        {/* Quality Profile */}
        {media?.qualityProfile && (
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-1">
              Quality Profile
            </h3>
            <p className="text-foreground">{media.qualityProfile}</p>
          </div>
        )}

        {/* Path */}
        {media?.path && (
          <div className="md:col-span-2">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-1">Path</h3>
            <p className="text-foreground text-sm font-mono bg-muted px-3 py-2 rounded break-all">
              {media.path}
            </p>
          </div>
        )}
      </div>

      {/* Cast */}
      {media?.cast && media.cast.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Cast</h3>
          <div className="flex flex-wrap gap-2">
            {media.cast.map((actor, index) => (
              <span key={index} className="px-3 py-1 bg-muted text-foreground text-sm rounded-md">
                {actor}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* External links */}
      {(jellyfinUrl || sonarrUrl || radarrUrl) && (
        <div>
          <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-3">Open in</h3>
          <div className="flex flex-wrap gap-2">
            {jellyfinUrl && (
              <a
                href={jellyfinUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-card border border-border rounded-lg text-sm text-foreground hover:bg-muted/50 hover:border-primary/40 transition-colors"
              >
                <Icon name="Play" size={14} className="text-primary" />
                Jellyfin
              </a>
            )}
            {sonarrUrl && (
              <a
                href={sonarrUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-card border border-border rounded-lg text-sm text-foreground hover:bg-muted/50 hover:border-primary/40 transition-colors"
              >
                <Icon name="Tv" size={14} className="text-primary" />
                Sonarr
              </a>
            )}
            {radarrUrl && (
              <a
                href={radarrUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-card border border-border rounded-lg text-sm text-foreground hover:bg-muted/50 hover:border-primary/40 transition-colors"
              >
                <Icon name="Film" size={14} className="text-primary" />
                Radarr
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MetadataPanel;
