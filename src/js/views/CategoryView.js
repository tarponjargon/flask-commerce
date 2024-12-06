//import { ssAfterResults } from "../services/AfterResults";

export default class CategoryView {
	constructor() {}
	init = view => {
		return new Promise(resolve => {
			resolve(view);
			// window.ssAfterResults = ssAfterResults;
			// afterLoad("Unbxd", () => {
			// 	CategoryResults();
			// 	resolve(view);
			// });
		});
	};
}
