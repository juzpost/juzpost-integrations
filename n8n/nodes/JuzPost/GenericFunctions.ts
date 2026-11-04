import type {
	IDataObject,
	IExecuteFunctions,
	IHookFunctions,
	IHttpRequestMethods,
	ILoadOptionsFunctions,
	IPollFunctions,
	IHttpRequestOptions,
	JsonObject,
} from 'n8n-workflow';
import { NodeApiError } from 'n8n-workflow';

export const BASE_URL = 'https://www.juzpost.com/api/cli/v1';

type Ctx = IExecuteFunctions | IHookFunctions | ILoadOptionsFunctions | IPollFunctions;

/** One authenticated call to the JuzPost REST API. Errors carry the API's own message. */
export async function juzPostApiRequest(
	this: Ctx,
	method: IHttpRequestMethods,
	endpoint: string,
	body: IDataObject = {},
	qs: IDataObject = {},
): Promise<IDataObject> {
	const options: IHttpRequestOptions = {
		method,
		url: `${BASE_URL}${endpoint}`,
		qs,
		body,
		json: true,
	};
	if (Object.keys(body).length === 0) delete options.body;
	if (Object.keys(qs).length === 0) delete options.qs;
	try {
		return (await this.helpers.httpRequestWithAuthentication.call(this, 'juzPostApi', options)) as IDataObject;
	} catch (error) {
		throw new NodeApiError(this.getNode(), error as JsonObject, {
			message: extractMessage(error),
		});
	}
}

/** Follows cursor pagination until exhausted or `limit` rows collected. */
export async function juzPostApiRequestAllItems(
	this: Ctx,
	endpoint: string,
	qs: IDataObject = {},
	limit = 0,
): Promise<IDataObject[]> {
	const out: IDataObject[] = [];
	let cursor: string | undefined;
	do {
		const page = await juzPostApiRequest.call(this, 'GET', endpoint, {}, {
			...qs,
			limit: 100,
			...(cursor ? { cursor } : {}),
		});
		out.push(...((page.data as IDataObject[]) ?? []));
		const pagination = (page.pagination as IDataObject) ?? {};
		cursor = pagination.hasMore ? (pagination.nextCursor as string) : undefined;
		if (limit && out.length >= limit) return out.slice(0, limit);
	} while (cursor);
	return out;
}

function extractMessage(error: unknown): string | undefined {
	const e = error as {
		error?: { error?: { message?: string } | string };
		response?: { body?: { error?: { message?: string } | string } };
		message?: string;
	};
	const inner = e?.error?.error ?? e?.response?.body?.error;
	if (typeof inner === 'string') return inner;
	if (inner && typeof inner === 'object' && inner.message) return inner.message;
	return e?.message;
}

/** Drops undefined, null and empty-string values so the API never sees them. */
export function clean(obj: IDataObject): IDataObject {
	return Object.fromEntries(
		Object.entries(obj).filter(([, v]) => v !== undefined && v !== null && v !== ''),
	);
}

/** Splits a comma-separated string into trimmed non-empty entries. */
export function csv(value: string | string[] | undefined): string[] | undefined {
	if (value === undefined || value === null) return undefined;
	const arr = Array.isArray(value) ? value : String(value).split(',');
	const out = arr.map((s) => String(s).trim()).filter(Boolean);
	return out.length ? out : undefined;
}
