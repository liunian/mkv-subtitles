#ifndef MKVSUBTITLES_H
#define MKVSUBTITLES_H

#include <QMap>

struct TreeNode {
	QString name;
	QString value;
	int level;
	QList<TreeNode *> children;

	~TreeNode() {
		qDeleteAll(children);
	}
};

struct SubtitleTrack {
	QString trackId;
	QString format;
	QString language;
};

namespace MkvUtils {
	TreeNode *parseMkvinfoOutput(const QString &output);

	TreeNode *findTracksNode(TreeNode *node);

	QList<QMap<QString, QString> > parseTracks(TreeNode *tracks);

	QList<SubtitleTrack> extractSubtitleTracksFromTree(TreeNode *root);

	QList<SubtitleTrack> getSubtitleTracks(const QString &mkvFile);

	void extractSingleSubtitle(const QString &mkvFile, const SubtitleTrack &track);

	void extractAllSubtitles(const QString &mkvFile, const QList<SubtitleTrack> &tracks);
}

#endif // MKVSUBTITLES_H
