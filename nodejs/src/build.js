/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	module.exports = __webpack_require__(1);


/***/ },
/* 1 */
/***/ function(module, exports) {

	// const todo = (state, action) => {
	//   switch (action.type) {
	//   case 'ADD_TODO':
	//     return {
	//       id: action.id,
	//       text: action.text,
	//       completed: false
	//     };
	//   case 'TOGGLE_TODO':
	//     if (state.id !== action.id) {
	//       return state;
	//     }

	//     return {
	//       ...state,
	//       completed: !state.completed
	//     };
	//   default:
	//     return state;
	//   }
	// };

	// const todos = (state = [], action) => {
	//   switch (action.type) {
	//   case 'ADD_TODO':
	//     return [
	//       ...state,
	//       todo(undefined, action)
	//     ];
	//   case 'TOGGLE_TODO':
	//     return state.map(t =>
	//       todo(t, action)
	//     );
	//   default:
	//     return state;
	//   }
	// };

	// const visibilityFilter = (
	//   state = 'SHOW_ALL',
	//   action
	// ) => {
	//   switch (action.type) {
	//   case 'SET_VISIBILITY_FILTER':
	//     return action.filter;
	//   default:
	//     return state;
	//   }
	// };

	// import {combineReducers} from 'Redux';
	// const todoApp = combineReducers({
	//   todos,
	//   visibilityFilter
	// });

	// import {createStore} from 'Redux';
	// const store = createStore(todoApp);

	// import {Component} from 'react';
	// import ReactDOM from 'react-dom';

	// let nextTodoId = 0;
	// class TodoApp extends Component {
	//   render() {
	//     return (
	//       <div>
	//         <input ref={node => {
	//           this.input = node;
	//         }} />
	//         <button onClick={() => {
	//           store.dispatch({
	//             type: 'ADD_TODO',
	//             text: this.input.value,
	//             id: nextTodoId
	//           });
	//           nextTodoId += 1;
	//           this.input.value = '';
	//         }}>
	//           Add Todo
	//         </button>
	//         <ul>
	//           {this.props.todos.map(todo =>
	//             <li key={todo.id}>{todo.text}</li>
	//           )}
	//         </ul>
	//       </div>
	//     );
	//   }
	// }

	// const render = () => {
	//   ReactDOM.render(
	//     <TodoApp todos={store.getState().todos} />,
	//     document.getElementById('app')
	//   );
	// };

	// store.subscribe(render);
	// render();

	const a = [1, 2, 3];
	const b = [...a, 4];
	console.log(b);


/***/ }
/******/ ]);