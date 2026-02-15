import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import Button from '../../components/ui/Button';
import HeroBanner from './components/HeroBanner';
import MetadataPanel from './components/MetadataPanel';
import EpisodesList from './components/EpisodesList';
import FileInfoPanel from './components/FileInfoPanel';
import { getLibraryItemById } from '../../services/libraryService';

const MediaDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [media, setMedia] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMedia = async () => {
      try {
        if (!id) {
          setLoading(false);
          return;
        }

        const data = await getLibraryItemById(id);

        console.log(data);

        // TODO: adapter `data` au format attendu par tes sous-composants.
        // Pour l'instant, je garde ton mock pour ne pas casser l'UI.
        const media = {
          id: data.id,
          title: data.title,
          mediaType: data.media_type,
          year: data.year,
          rating: data.rating,
          runtime: '49 min',
          genres: ['Crime', 'Drama', 'Thriller'],
          overview: data.description,
          image: data.image_url,
          backdropImage: data.image_url,
          status: 'Ended',
          network: 'AMC',
          nbMedia: data.nb_media,

          // File Information
          fileInfo: {
            path: '/media/tv/Breaking Bad',
            size: data.size,
            quality: '1080p BluRay',
            videoCodec: 'x264',
            audioCodec: 'AC3 5.1',
            container: 'MKV',
            subtitles: [
              { language: 'English', format: 'SRT', forced: false },
              { language: 'Spanish', format: 'SRT', forced: false },
              { language: 'French', format: 'SRT', forced: false },
            ],

            torrentInfo: {
              client: 'qBittorrent',
              seedRatio: data.torrent_info[0].ratio,
              status: data.torrent_info[0].status,
            },
          },

          // Monitoring Status
          monitored: true,
          downloadedEpisodes: 62,
          totalEpisodes: 62,
          missingEpisodes: 0,

          // Seasons and Episodes
          seasons: [
            {
              seasonNumber: 1,
              episodeCount: 7,
              episodes: [
                {
                  episodeNumber: 1,
                  title: 'Pilot',
                  airDate: '2008-01-20',
                  overview:
                    'When an unassuming high school chemistry teacher discovers he has a rare form of lung cancer, he decides to team up with a former student and create a top of the line crystal meth.',
                  runtime: 58,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '2.1 GB',
                  quality: '1080p BluRay',
                  watched: true,
                },
                {
                  episodeNumber: 2,
                  title: "Cat's in the Bag...",
                  airDate: '2008-01-27',
                  overview:
                    "Walt and Jesse attempt to tie up loose ends. The desperate situation gets more complicated with the flip of a coin. Walt's wife, Skyler, becomes suspicious of Walt's strange behavior.",
                  runtime: 48,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '1.9 GB',
                  quality: '1080p BluRay',
                  watched: true,
                },
                {
                  episodeNumber: 3,
                  title: "...And the Bag's in the River",
                  airDate: '2008-02-10',
                  overview:
                    'Walter fights with Jesse over his drug use, causing him to leave Walter alone with their captive, Krazy-8. Meanwhile, Hank has a scared straight moment with Walter Jr. after his aunt discovers he has been smoking pot.',
                  runtime: 48,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '2.0 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
                {
                  episodeNumber: 4,
                  title: 'Cancer Man',
                  airDate: '2008-02-17',
                  overview:
                    'Walter finally tells his family that he has been stricken with cancer. Meanwhile, the DEA believes Albuquerque has a new, big time player to worry about. Meanwhile, a worthy recipient is the target of a depressed Walter\'s anger.',
                  runtime: 48,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '1.8 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
                {
                  episodeNumber: 5,
                  title: 'Gray Matter',
                  airDate: '2008-02-24',
                  overview:
                    "Walter and Skyler attend a former colleague's party. Jesse tries to free himself from the drugs, while Skyler organizes an intervention.",
                  runtime: 48,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '2.0 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
                {
                  episodeNumber: 6,
                  title: "Crazy Handful of Nothin'",
                  airDate: '2008-03-02',
                  overview:
                    'The side effects of chemo begin to plague Walt. Meanwhile, the DEA rounds up suspected dealers.',
                  runtime: 48,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '1.9 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
                {
                  episodeNumber: 7,
                  title: 'A No-Rough-Stuff-Type Deal',
                  airDate: '2008-03-09',
                  overview:
                    "Walter accepts his new identity as a drug dealer after a PTA meeting. Elsewhere, Jesse decides to put his aunt's house on the market and Skyler is the recipient of a baby shower.",
                  runtime: 48,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '2.1 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
              ],
            },
            {
              seasonNumber: 2,
              episodeCount: 13,
              episodes: [
                {
                  episodeNumber: 1,
                  title: 'Seven Thirty-Seven',
                  airDate: '2009-03-08',
                  overview:
                    'Walt and Jesse realize how dire their situation is. They must come up with a plan to kill Tuco before Tuco kills them first.',
                  runtime: 47,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '2.0 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
                {
                  episodeNumber: 2,
                  title: 'Grilled',
                  airDate: '2009-03-15',
                  overview:
                    "Walt and Jesse are vividly reminded of Tuco's volatile nature, and try to figure a way out of their business partnership.",
                  runtime: 47,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '1.9 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
              ],
            },
            {
              seasonNumber: 3,
              episodeCount: 13,
              episodes: [
                {
                  episodeNumber: 1,
                  title: 'No Más',
                  airDate: '2010-03-21',
                  overview:
                    'Walt faces a new threat on a new front and deals with an increasingly angry Skyler, who must consider what to do next with her life and the kids.',
                  runtime: 47,
                  downloaded: true,
                  monitored: true,
                  hasSubtitles: true,
                  fileSize: '2.1 GB',
                  quality: '1080p BluRay',
                  watched: false,
                },
              ],
            },
          ],
        };

        // Pour le moment, on ignore `data` et on affiche le mock
        setMedia(media);
      } catch (error) {
        console.error('Failed to fetch media detail', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMedia();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="text-muted-foreground">Loading media details...</p>
        </div>
      </div>
    );
  }

  if (!media) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Media not found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Banner */}
      <HeroBanner media={media} />

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6 md:py-8 space-y-6">
        {/* Back Button */}
        <Button
          variant="ghost"
          size="sm"
          iconName="ArrowLeft"
          onClick={() => navigate('/library')}
        >
          Back to Library
        </Button>

        {/* Metadata and File Info Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Metadata Panel */}
          <div className="lg:col-span-2">
            <MetadataPanel media={media} />
          </div>

          {/* File Info Panel */}
          <div className="lg:col-span-1">
            <FileInfoPanel media={media} />
          </div>
        </div>

        {/* Episodes List (TV Shows Only) */}
        {media?.mediaType === 'tv' && media?.seasons && (
          <EpisodesList seasons={media.seasons} />
        )}
      </div>
    </div>
  );
};

export default MediaDetail;
