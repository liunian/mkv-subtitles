#pragma once

#include <QStandardItemModel>
#include "ui_MkvSubtitles.h"
#include "mkv.h"

class MkvSubtitles final : public QMainWindow {
	Q_OBJECT

public:
	explicit MkvSubtitles(QWidget *parent = nullptr);

	~MkvSubtitles() override = default;

public slots:
	void on_btnFilePick_clicked();

	void on_btnExtract_clicked();

	//void updateSelectedTrack(int index);
	void onCheckedStateChanged(const QModelIndex &topLeft, const QModelIndex &bottomRight,
	                           const QVector<int> &roles) const;

private:
	void updateTracks() const;

	static QString getTrackTitle(const SubtitleTrack &track);

	Ui::MkvSubtitlesClass *ui;
	QString filePath;
	QStandardItemModel *tracksModel;
};
