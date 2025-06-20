#include <iostream>
#include <QFileDialog>
#include <QMessagebox>
#include "mkv.h"
#include "MkvSubtitles.h"

#include "checkableDelegate.h"

using namespace std;

MkvSubtitles::MkvSubtitles(QWidget *parent)
	: QMainWindow(parent),
	  ui(new Ui::MkvSubtitlesClass),
	  tracksModel(new QStandardItemModel(this)) {
	ui->setupUi(this);

	const auto listView = this->ui->listTracks;
	listView->setModel(this->tracksModel);
	listView->setSelectionMode(QAbstractItemView::MultiSelection);
	listView->setItemDelegate(new CheckableDelegate(listView));
	listView->setEditTriggers(QAbstractItemView::NoEditTriggers);

	connect(this->tracksModel, &QAbstractItemModel::dataChanged, this, &MkvSubtitles::onCheckedStateChanged);
}

void MkvSubtitles::on_btnFilePick_clicked() {
	const auto fileName = QFileDialog::getOpenFileName(this, tr("选择 MKV 文件"), QDir::homePath(), tr("MKV Files (*.mkv)"));

	if (fileName.isEmpty()) return;

	this->filePath = fileName;
	ui->labelFile->setText(QDir::toNativeSeparators(fileName));
	this->updateTracks();
}

void MkvSubtitles::on_btnExtract_clicked() {
	const auto model = this->tracksModel;
	// 只需要一个
	const auto checkedIndices = model->match(
		model->index(0, 0), // 起始位置
		Qt::CheckStateRole, // 角色
		Qt::Checked, // 目标值
		-1, // 最多返回 1
		Qt::MatchExactly // 精确匹配
	);

	if (!checkedIndices.isEmpty()) {
		QList<SubtitleTrack> tracks;
		for (const auto index : checkedIndices) {
			const auto track = qvariant_cast<SubtitleTrack>(model->data(index, Qt::UserRole));
			tracks.append(track);
		}

		this->ui->statusBar->showMessage("正在提取字幕");
		MkvUtils::extractAllSubtitles(this->filePath, tracks);
		this->ui->statusBar->clearMessage();
		QMessageBox::information(this, tr("完成"), tr("字幕已提取到视频所在目录"));
	}
}

void MkvSubtitles::onCheckedStateChanged(const QModelIndex &topLeft, const QModelIndex &bottomRight,
                                         const QVector<int> &roles) const {
	Q_UNUSED(topLeft);
	Q_UNUSED(bottomRight);

	// 检查是否是 CheckStateRole 变化
	if (roles.contains(Qt::CheckStateRole)) {
		const auto model = this->tracksModel;
		// 只需要一个
		const auto checkedIndices = model->match(
			model->index(0, 0), // 起始位置
			Qt::CheckStateRole, // 角色
			Qt::Checked, // 目标值
			1, // 最多返回 1
			Qt::MatchExactly // 精确匹配
		);

		const auto hasChecked = !checkedIndices.isEmpty();
		ui->btnExtract->setEnabled(hasChecked);
	}
}

void MkvSubtitles::updateTracks() const {
	this->ui->statusBar->showMessage("正在解析字幕轨道");
	auto tracks = MkvUtils::getSubtitleTracks(this->filePath);

	const auto model = this->tracksModel;
	model->clear();
	for (const auto &track: tracks) {
		const auto item = new QStandardItem(getTrackTitle(track));
		item->setData(QVariant::fromValue(track), Qt::UserRole);
		item->setCheckable(true);

		model->appendRow(item);
	}
	this->ui->statusBar->clearMessage();
}

QString MkvSubtitles::getTrackTitle(const SubtitleTrack &track) {
	return QStringLiteral("Track ID: %1, Format: %2, Language: %3")
			.arg(track.trackId)
			.arg(track.format)
			.arg(track.language);
}
