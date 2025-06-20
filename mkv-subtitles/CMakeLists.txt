cmake_minimum_required(VERSION 3.16)
project(mkv-subtitles LANGUAGES CXX)

include(qt.cmake)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core)
find_package(Qt${QT_VERSION_MAJOR}
    COMPONENTS
        Core
        Gui
        Widgets
)
qt_standard_project_setup()

set(PROJECT_SOURCES
    src/main.cpp
    src/MkvSubtitles.ui
    src/mkv.h
    src/mkv.cpp
    src/MkvSubtitles.h
    src/MkvSubtitles.cpp
        src/checkableDelegate.h
)

qt_add_executable(${PROJECT_NAME} ${PROJECT_SOURCES})

if(WIN32)
    set(APP_ICON_RESOURCE_WINDOWS "${CMAKE_CURRENT_SOURCE_DIR}/mkv-subtitles.rc")
    target_sources(${PROJECT_NAME} PRIVATE ${APP_ICON_RESOURCE_WINDOWS})
endif()

set_target_properties(${PROJECT_NAME}
    PROPERTIES
        WIN32_EXECUTABLE TRUE
)

target_link_libraries(${PROJECT_NAME}
    PUBLIC
        Qt::Core
        Qt::Gui
        Qt::Widgets
)

# --------------------------
# 跨平台 Release 和打包
# --------------------------

# 设置安装目录结构
if(WIN32 OR UNIX)
    install(TARGETS ${PROJECT_NAME} RUNTIME DESTINATION bin)
elseif(APPLE)
    # macOS 下打包为 .app Bundle
    set_target_properties(${PROJECT_NAME} PROPERTIES
            MACOSX_BUNDLE TRUE
            MACOSX_BUNDLE_BUNDLE_NAME "${PROJECT_NAME}"
    )
    install(TARGETS ${PROJECT_NAME} BUNDLE DESTINATION .)
endif()

# --------------------------
# 添加 Qt 运行时依赖处理脚本
# --------------------------

# Windows: 自动运行 windeployqt
if(WIN32)
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
            COMMAND windeployqt "$<TARGET_FILE:${PROJECT_NAME}>"
            COMMENT "Running windeployqt..."
    )
endif()

# macOS: 自动运行 macdeployqt
if(APPLE)
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
            COMMAND macdeployqt "$<TARGET_BUNDLE_DIR:${PROJECT_NAME}>"
            COMMENT "Running macdeployqt..."
    )
endif()

# --------------------------
# CPack 跨平台打包配置
# --------------------------

include(InstallRequiredSystemLibraries)

set(CPACK_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_PACKAGE_VENDOR "Liu Nian")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_CONTACT "cunxingbo@outlook.com")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "MKV 字幕提取器")

# 平台特定打包格式
if(WIN32)
    set(CPACK_GENERATOR "NSIS")
    set(CPACK_NSIS_DISPLAY_NAME "${PROJECT_NAME} Installer")
    set(CPACK_NSIS_PACKAGE_NAME "${PROJECT_NAME} Installer")
    set(CPACK_NSIS_EXECUTABLES_DIRECTORY ".")
elseif(APPLE)
    set(CPACK_GENERATOR "DragNDrop")
    set(CPACK_BUNDLE_NAME "${PROJECT_NAME}")
    set(CPACK_BUNDLE_STARTUP_COMMAND "${PROJECT_NAME}.app/Contents/MacOS/${PROJECT_NAME}")
elseif(UNIX)
    set(CPACK_GENERATOR "DEB;TGZ")
    set(CPACK_DEBIAN_PACKAGE_MAINTAINER "Liu Nian") # Required for DEB
    set(CPACK_DEBIAN_PACKAGE_DEPENDS "qt6-base")
    set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-linux")
endif()

include(CPack)