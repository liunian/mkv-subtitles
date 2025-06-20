#include "MkvSubtitles.h"
#include <QtWidgets/QApplication>

int main(int argc, char *argv[]) {
	QApplication a(argc, argv);
	MkvSubtitles w;
	w.show();
	return a.exec();
}
