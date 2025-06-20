//
// Created by Neal on 2025/6/20.
//

#ifndef CHECKABLEDELEGATE_H
#define CHECKABLEDELEGATE_H

#include <QStyledItemDelegate>
#include <QEvent>

class CheckableDelegate final : public QStyledItemDelegate {
public:
	using QStyledItemDelegate::QStyledItemDelegate;

	bool editorEvent(QEvent *event, QAbstractItemModel *model,
	                 const QStyleOptionViewItem &option, const QModelIndex &index) override {
		if (event->type() == QEvent::MouseButtonRelease) {
			// 如果是鼠标点击事件，切换复选框状态
			const auto state = static_cast<Qt::CheckState>(index.data(Qt::CheckStateRole).toInt());
			model->setData(index, state == Qt::Checked ? Qt::Unchecked : Qt::Checked, Qt::CheckStateRole);
			return true; // 事件已处理
		}
		return QStyledItemDelegate::editorEvent(event, model, option, index);
	}
};


#endif //CHECKABLEDELEGATE_H
