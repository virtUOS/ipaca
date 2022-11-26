# from example: https://www.anychart.com/products/anychart/gallery/Column_Charts/Stacked_Column_Chart.php
def createBarChartConfig(container_name, series): 
    chart = {
        "chart": {
            "container": container_name,
            "type": "column",
            "zIndex": 0,
            "enabled": True,
            "title": "Test",
            "baseline": 0,
            "barGroupsPadding": 0.8,
            "barsPadding": 0.4,
            "xScale": 0,
            "yScale": 1,
            "palette": {
                "type": "distinct",
                "items": [
                    "#8fce00",
                    "#f44336"
                ]
            },
            "series": series,
            "xAxes": [
                {
                    "enabled": True,
                    "drawFirstLabel": True,
                    "drawLastLabel": True,
                    "overlapMode": "no-overlap",
                    "stroke": "#CECECE",
                    "orientation": "bottom",
                    "title": {
                        "fontSize": 13,
                        "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                        "fontColor": "#545f69",
                        "fontOpacity": 1,
                        "vAlign": "top",
                        "hAlign": "center",
                        "align": "center",
                        "text": "Date",
                    },
                    "labels": {
                        "zIndex": 35,
                        "enabled": True
                    },
                    "minorLabels": {
                        "zIndex": 35,
                        "enabled": True
                    },
                    "ticks": {
                        "zIndex": 35,
                        "enabled": True,
                        "stroke": "#CECECE",
                        "length": 6,
                        "position": "outside"
                    },
                    "minorTicks": {
                        "zIndex": 35,
                        "enabled": True,
                        "stroke": "#EAEAEA",
                        "length": 4,
                        "position": "outside"
                    },
                    "scale": 0
                }
            ],
            "yAxes": [
                {
                    "enabled": True,
                    "drawFirstLabel": True,
                    "drawLastLabel": True,
                    "overlapMode": "no-overlap",
                    "stroke": "#CECECE",
                    "orientation": "left",
                    "title": {
                        "zIndex": 35,
                        "enabled": True,
                        "fontSize": 13,
                        "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                        "fontColor": "#545f69",
                        "fontOpacity": 1,
                        "vAlign": "top",
                        "hAlign": "center",
                        "align": "center",
                        "text": "Num Solutions",
                    },
                    "labels": {
                        "zIndex": 35,
                        "enabled": True,
                        "format": "{%Value}{groupsSeparator: }"
                    },
                    "minorLabels": {
                        "zIndex": 35,
                        "enabled": False
                    },
                    "ticks": {
                        "zIndex": 35,
                        "enabled": True,
                        "stroke": "#CECECE",
                        "length": 6,
                        "position": "outside"
                    },
                    "minorTicks": {
                        "zIndex": 35,
                        "enabled": False,
                        "stroke": "#EAEAEA",
                        "length": 4,
                        "position": "outside"
                    },
                    "scale": 1
                }
            ],
            "scales": [
                {
                    "type": "date-time",
                    "inverted": False,
                    "ticks": {
                        "interval": "P1Y"
                    },
                    "minorTicks": {
                        "interval": "P1M"
                    },
                    "mode": "discrete"
                },
                {
                    "type": "linear",
                    "inverted": False,
                    "maximum": None,
                    "minimum": None,
                    "minimumGap": 0.1,
                    "maximumGap": 0.1,
                    "softMinimum": 0,
                    "softMaximum": None,
                    "alignMinimum": True,
                    "alignMaximum": True,
                    "maxTicksCount": 1000,
                    "ticks": {
                        "mode": "linear",
                        "base": 0,
                        "allowFractional": True,
                        "minCount": 4,
                        "maxCount": 6
                    },
                    "minorTicks": {
                        "mode": "linear",
                        "base": 0,
                        "allowFractional": True,
                        "count": 5
                    },
                    "stackMode": "value",
                    "stackDirection": "direct",
                    "stickToZero": True,
                    "comparisonMode": "none"
                }
            ],
            "xScroller": {
                "zIndex": 35,
                "enabled": True,
                "height": 16,
                "minHeight": None,
                "maxHeight": None,
                "orientation": "bottom",
                "inverted": False,
                "autoHide": False,
                "fill": "#f7f7f7",
                "selectedFill": "#ddd",
                "outlineStroke": "none",
                "allowRangeChange": True,
                "thumbs": {
                    "normal": {
                        "fill": "#E9E9E9",
                        "stroke": "#7c868e"
                    },
                    "hovered": {
                        "fill": "#ffffff",
                        "stroke": "#757575"
                    },
                    "enabled": True,
                    "autoHide": False
                },
                "position": "after-axes"
            },
            "xZoom": {
                "startValue": "2022-1-1",
                "endValue": "2023-1-1",
                "continuous": True
            },
            "legend": {
                "zIndex": 200,
                "enabled": True,
                "fontSize": 13,
                "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                "fontColor": "#7c868e",
                "fontOpacity": 1,
                "vAlign": "bottom",
                "hAlign": "start",
                "textOverflow": "...",
                "selectable": False,
                "disablePointerEvents": False,
                "useHtml": False,
                "inverted": False,
                "itemsLayout": "horizontal",
                "iconSize": 15,
                "position": "top",
                "positionMode": "outside",
                "drag": False,
                "itemsHAlign": "left",
                "itemsSpacing": 15,
                "itemsSourceMode": "default",
                "hoverCursor": "pointer",
                "iconTextSpacing": 5,
                "align": "center",
                "margin": {
                    "left": 0,
                    "top": 0,
                    "bottom": 0,
                    "right": 0
                },
                "padding": {
                    "left": 0,
                    "top": 0,
                    "bottom": 20,
                    "right": 0
                },
                "paginator": {
                    "zIndex": 30,
                    "enabled": True,
                    "fontSize": 12,
                    "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                    "fontColor": "#545f69",
                    "fontOpacity": 1,
                    "vAlign": "top",
                    "hAlign": "start",
                    "textOverflow": "",
                    "selectable": False,
                    "disablePointerEvents": False,
                    "useHtml": False,
                    "orientation": "right",
                    "layout": "horizontal",
                    "padding": {
                        "left": 5,
                        "top": 0,
                        "bottom": 0,
                        "right": 0
                    },
                    "margin": {
                        "left": 0,
                        "top": 0,
                        "bottom": 0,
                        "right": 0
                    }
                },
            },
        }
    }

    return chart

def createDonutChartConfig(title, container, data):
    chart = {
        "chart": {
            "container": container,
            "zIndex": 0,
            "enabled": True,
            "type": "pie",
            "title": {
                "zIndex": 80,
                "enabled": True,
                "fontSize": 16,
                "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                "fontColor": "#7c868e",
                "fontOpacity": 1,
                "textIndent": 0,
                "vAlign": "top",
                "hAlign": "center",
                "selectable": False,
                "disablePointerEvents": False,
                "useHtml": False,
                "align": "center",
                "text": title,
                "padding": {
                    "left": 0,
                    "top": 0,
                    "bottom": 10,
                    "right": 0
                },
            },
            "padding": {
                "left": 10,
                "top": 10,
                "bottom": 15,
                "right": 20
            },
            "autoRedraw": True,
            "selectRectangleMarqueeFill": {
                "color": "#d3d3d3",
                "opacity": 0.4
            },
            "selectRectangleMarqueeStroke": "#d3d3d3",
            "legend": {
                "zIndex": 200,
                "enabled": True,
                "fontSize": 12,
                "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                "fontColor": "#7c868e",
                "fontOpacity": 1,
                "vAlign": "bottom",
                "hAlign": "start",
                "selectable": False,
                "disablePointerEvents": False,
                "useHtml": False,
                "inverted": False,
                "itemsLayout": "horizontal",
                "iconSize": 15,
                "position": "bottom",
                "positionMode": "outside",
                "drag": False,
                "itemsHAlign": "left",
                "itemsSpacing": 15,
                "itemsSourceMode": "default",
                "hoverCursor": "pointer",
                "iconTextSpacing": 5,
                "align": "center",
                "padding": {
                    "left": 10,
                    "top": 10,
                    "bottom": 0,
                    "right": 10
                },
                "background": {
                    "enabled": False
                },
                "title": {
                    "enabled": False,
                    "maxLength": None,
                    "fontSize": 15,
                    "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                    "fontColor": "#7c868e",
                    "fontOpacity": 1,
                    "vAlign": "top",
                    "hAlign": "center",
                    "textOverflow": "",
                    "selectable": False,
                    "disablePointerEvents": False,
                    "useHtml": False,
                    "align": "center",
                    "text": "Title text",
                },
                "titleSeparator": {
                    "zIndex": 1,
                    "enabled": False,
                    "fill": {
                        "color": "#CECECE",
                        "opacity": 0.3
                    },
                    "stroke": "none",
                    "width": "100%",
                    "height": 1,
                    "orientation": "top",
                    "margin": {
                        "left": 0,
                        "top": 5,
                        "bottom": 5,
                        "right": 0
                    }
                },
                "paginator": {
                    "zIndex": 30,
                    "enabled": True,
                    "fontSize": 12,
                    "fontFamily": "Verdana, Helvetica, Arial, sans-serif",
                    "fontColor": "#545f69",
                    "fontOpacity": 1,
                    "vAlign": "top",
                    "hAlign": "start",
                    "textOverflow": "",
                    "selectable": False,
                    "disablePointerEvents": False,
                    "useHtml": False,
                    "orientation": "right",
                    "layout": "horizontal",
                    "padding": {
                        "left": 5,
                        "top": 0,
                        "bottom": 0,
                        "right": 0
                    },
                },
            },
            "interactivity": {
                "spotRadius": 2,
                "multiSelectOnClick": True,
                "unselectOnClickOutOfPoint": False,
                "hoverMode": "single",
                "selectionMode": "multi-select"
            },
            "data": data,
            "palette": {
                "type": "distinct",
                "items": [
                    "#64b5f6",
                    "#1976d2",
                    "#ef6c00",
                    "#ffd54f",
                    "#455a64",
                    "#96a6a6",
                    "#dd2c00",
                    "#00838f",
                    "#00bfa5",
                    "#ffa000"
                ]
            },
            "center": {
                "stroke": "none",
                "fill": "none"
            },
            "overlapMode": "no-overlap",
            "startAngle": 0,
            "radius": "43%",
            "innerRadius": "30%",
            "sort": "none",
            "insideLabelsOffset": "50%",
            "connectorLength": 20,
            "outsideLabelsCriticalAngle": 60,
            "forceHoverLabels": True,
            "connectorStroke": "#CECECE",
            "mode3d": False,
        }
    }

    return chart

                