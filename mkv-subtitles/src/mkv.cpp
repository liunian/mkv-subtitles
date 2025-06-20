#include "mkv.h"
#include <QProcess>
#include <QRegularExpression>
#include <QDebug>

TreeNode *MkvUtils::parseMkvinfoOutput(const QString &output) {
	const auto root = new TreeNode{"root", QString(), 0, {}};
	QList stack = {root};

	const auto lines = output.split('\n', Qt::SkipEmptyParts);
	const QRegularExpression re(R"(\|\s*\+)");

	for (const QString &line: lines) {
		const int level = line.startsWith('+') ? 1 : re.match(line).capturedLength();
		if (level == 0) continue;

		auto processedLine = line.trimmed().remove('|').remove('+').trimmed();
		const auto index = processedLine.indexOf(':');
		QString name = processedLine;
		auto value = QString();
		if (index != -1) {
			name = processedLine.left(index);
			value = processedLine.mid(index + 1).trimmed();
		}

		while (!stack.isEmpty() && stack.last()->level >= level) {
			stack.removeLast();
		}

		if (stack.isEmpty() || stack.last()->level + 1 != level) {
			qWarning() << "Invalid tree level in line:" << line;
			continue;
		}

		const auto node = new TreeNode{name, value, level, {}};
		stack.last()->children.append(node);
		stack.append(node);
	}
	return root;
}

TreeNode *MkvUtils::findTracksNode(TreeNode *node) {
	if (node->name == "Tracks") return node;
	for (const auto child: node->children) {
		if (const auto result = findTracksNode(child)) {
			return result;
		}
	}
	return nullptr;
}

QList<QMap<QString, QString> > MkvUtils::parseTracks(TreeNode *tracks) {
	QList<QMap<QString, QString> > result;
	for (const auto track: tracks->children) {
		QMap<QString, QString> item;
		for (const auto prop: track->children) {
			item[prop->name] = prop->value;
		}
		result.append(item);
	}
	return result;
}

QList<SubtitleTrack> MkvUtils::extractSubtitleTracksFromTree(TreeNode *root) {
	QList<SubtitleTrack> subtitles;
	if (const auto tracksNode = findTracksNode(root)) {
		const QRegularExpression re(R"(track ID for mkvmerge & mkvextract: (\d+))");

		for (const auto &track: parseTracks(tracksNode)) {
			if (track["Track type"] != "subtitles") continue;

			QRegularExpressionMatch match = re.match(track["Track number"]);
			if (!match.hasMatch()) continue;

			subtitles.append({
				match.captured(1),
				track["Codec ID"],
				track.value("Language (IETF BCP 47)", "und") // 默认语言为undefined
			});
		}
	}
	return subtitles;
}

QList<SubtitleTrack> MkvUtils::getSubtitleTracks(const QString &mkvFile) {
	QProcess process;
	process.start("mkvinfo", {"--ui-language", "en", mkvFile});
	process.waitForFinished();
	const auto tree = parseMkvinfoOutput(QString::fromUtf8(process.readAllStandardOutput()));
	auto tracks = extractSubtitleTracksFromTree(tree);
	delete tree;
	return tracks;
}

void MkvUtils::extractSingleSubtitle(const QString &mkvFile, const SubtitleTrack &track) {
	static const QMap<QString, QString> formatMap = {
		{"S_TEXT/UTF8", "srt"}, {"S_TEXT/ASS", "ass"}, {"S_TEXT/SSA", "ssa"}
	};

	auto ext = formatMap.value(track.format, "srt");
	auto outputPath = QString("%1_%2.%3")
			.arg(mkvFile.left(mkvFile.lastIndexOf('.')), track.language, ext);

	QProcess::execute("mkvextract", {
		                  "tracks", mkvFile, QString("%1:%2").arg(track.trackId, outputPath)
	                  });
}

void MkvUtils::extractAllSubtitles(const QString &mkvFile, const QList<SubtitleTrack> &tracks) {
	for (const auto &track: tracks) {
		extractSingleSubtitle(mkvFile, track);
	}
}
