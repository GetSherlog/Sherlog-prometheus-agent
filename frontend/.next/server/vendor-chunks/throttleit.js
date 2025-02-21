"use strict";
/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
exports.id = "vendor-chunks/throttleit";
exports.ids = ["vendor-chunks/throttleit"];
exports.modules = {

/***/ "(ssr)/./node_modules/throttleit/index.js":
/*!******************************************!*\
  !*** ./node_modules/throttleit/index.js ***!
  \******************************************/
/***/ ((module) => {

eval("\nfunction throttle(function_, wait) {\n    if (typeof function_ !== \"function\") {\n        throw new TypeError(`Expected the first argument to be a \\`function\\`, got \\`${typeof function_}\\`.`);\n    }\n    // TODO: Add `wait` validation too in the next major version.\n    let timeoutId;\n    let lastCallTime = 0;\n    return function throttled(...arguments_) {\n        clearTimeout(timeoutId);\n        const now = Date.now();\n        const timeSinceLastCall = now - lastCallTime;\n        const delayForNextCall = wait - timeSinceLastCall;\n        if (delayForNextCall <= 0) {\n            lastCallTime = now;\n            function_.apply(this, arguments_);\n        } else {\n            timeoutId = setTimeout(()=>{\n                lastCallTime = Date.now();\n                function_.apply(this, arguments_);\n            }, delayForNextCall);\n        }\n    };\n}\nmodule.exports = throttle;\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHNzcikvLi9ub2RlX21vZHVsZXMvdGhyb3R0bGVpdC9pbmRleC5qcyIsIm1hcHBpbmdzIjoiO0FBQUEsU0FBU0EsU0FBU0MsU0FBUyxFQUFFQyxJQUFJO0lBQ2hDLElBQUksT0FBT0QsY0FBYyxZQUFZO1FBQ3BDLE1BQU0sSUFBSUUsVUFBVSxDQUFDLHdEQUF3RCxFQUFFLE9BQU9GLFVBQVUsR0FBRyxDQUFDO0lBQ3JHO0lBRUEsNkRBQTZEO0lBRTdELElBQUlHO0lBQ0osSUFBSUMsZUFBZTtJQUVuQixPQUFPLFNBQVNDLFVBQVUsR0FBR0MsVUFBVTtRQUN0Q0MsYUFBYUo7UUFFYixNQUFNSyxNQUFNQyxLQUFLRCxHQUFHO1FBQ3BCLE1BQU1FLG9CQUFvQkYsTUFBTUo7UUFDaEMsTUFBTU8sbUJBQW1CVixPQUFPUztRQUVoQyxJQUFJQyxvQkFBb0IsR0FBRztZQUMxQlAsZUFBZUk7WUFDZlIsVUFBVVksS0FBSyxDQUFDLElBQUksRUFBRU47UUFDdkIsT0FBTztZQUNOSCxZQUFZVSxXQUFXO2dCQUN0QlQsZUFBZUssS0FBS0QsR0FBRztnQkFDdkJSLFVBQVVZLEtBQUssQ0FBQyxJQUFJLEVBQUVOO1lBQ3ZCLEdBQUdLO1FBQ0o7SUFDRDtBQUNEO0FBRUFHLE9BQU9DLE9BQU8sR0FBR2hCIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vc2hlcmxvZy1mcm9udGVuZC8uL25vZGVfbW9kdWxlcy90aHJvdHRsZWl0L2luZGV4LmpzPzdkYzgiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gdGhyb3R0bGUoZnVuY3Rpb25fLCB3YWl0KSB7XG5cdGlmICh0eXBlb2YgZnVuY3Rpb25fICE9PSAnZnVuY3Rpb24nKSB7XG5cdFx0dGhyb3cgbmV3IFR5cGVFcnJvcihgRXhwZWN0ZWQgdGhlIGZpcnN0IGFyZ3VtZW50IHRvIGJlIGEgXFxgZnVuY3Rpb25cXGAsIGdvdCBcXGAke3R5cGVvZiBmdW5jdGlvbl99XFxgLmApO1xuXHR9XG5cblx0Ly8gVE9ETzogQWRkIGB3YWl0YCB2YWxpZGF0aW9uIHRvbyBpbiB0aGUgbmV4dCBtYWpvciB2ZXJzaW9uLlxuXG5cdGxldCB0aW1lb3V0SWQ7XG5cdGxldCBsYXN0Q2FsbFRpbWUgPSAwO1xuXG5cdHJldHVybiBmdW5jdGlvbiB0aHJvdHRsZWQoLi4uYXJndW1lbnRzXykgeyAvLyBlc2xpbnQtZGlzYWJsZS1saW5lIGZ1bmMtbmFtZXNcblx0XHRjbGVhclRpbWVvdXQodGltZW91dElkKTtcblxuXHRcdGNvbnN0IG5vdyA9IERhdGUubm93KCk7XG5cdFx0Y29uc3QgdGltZVNpbmNlTGFzdENhbGwgPSBub3cgLSBsYXN0Q2FsbFRpbWU7XG5cdFx0Y29uc3QgZGVsYXlGb3JOZXh0Q2FsbCA9IHdhaXQgLSB0aW1lU2luY2VMYXN0Q2FsbDtcblxuXHRcdGlmIChkZWxheUZvck5leHRDYWxsIDw9IDApIHtcblx0XHRcdGxhc3RDYWxsVGltZSA9IG5vdztcblx0XHRcdGZ1bmN0aW9uXy5hcHBseSh0aGlzLCBhcmd1bWVudHNfKTtcblx0XHR9IGVsc2Uge1xuXHRcdFx0dGltZW91dElkID0gc2V0VGltZW91dCgoKSA9PiB7XG5cdFx0XHRcdGxhc3RDYWxsVGltZSA9IERhdGUubm93KCk7XG5cdFx0XHRcdGZ1bmN0aW9uXy5hcHBseSh0aGlzLCBhcmd1bWVudHNfKTtcblx0XHRcdH0sIGRlbGF5Rm9yTmV4dENhbGwpO1xuXHRcdH1cblx0fTtcbn1cblxubW9kdWxlLmV4cG9ydHMgPSB0aHJvdHRsZTtcbiJdLCJuYW1lcyI6WyJ0aHJvdHRsZSIsImZ1bmN0aW9uXyIsIndhaXQiLCJUeXBlRXJyb3IiLCJ0aW1lb3V0SWQiLCJsYXN0Q2FsbFRpbWUiLCJ0aHJvdHRsZWQiLCJhcmd1bWVudHNfIiwiY2xlYXJUaW1lb3V0Iiwibm93IiwiRGF0ZSIsInRpbWVTaW5jZUxhc3RDYWxsIiwiZGVsYXlGb3JOZXh0Q2FsbCIsImFwcGx5Iiwic2V0VGltZW91dCIsIm1vZHVsZSIsImV4cG9ydHMiXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///(ssr)/./node_modules/throttleit/index.js\n");

/***/ })

};
;