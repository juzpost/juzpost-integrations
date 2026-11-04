import type {
	IDataObject,
	IExecuteFunctions,
	ILoadOptionsFunctions,
	INodeExecutionData,
	INodePropertyOptions,
	INodeType,
	INodeTypeDescription,
} from 'n8n-workflow';
import { NodeConnectionTypes, NodeOperationError } from 'n8n-workflow';

import { clean, csv, juzPostApiRequest, juzPostApiRequestAllItems } from './GenericFunctions';

const PLATFORMS = [
	'youtube',
	'tiktok',
	'instagram',
	'facebook',
	'x',
	'linkedin',
	'pinterest',
	'threads',
	'bluesky',
	'tumblr',
	'wordpress',
];

const show = (resource: string, operation?: string | string[]) => ({
	show: {
		resource: [resource],
		...(operation ? { operation: Array.isArray(operation) ? operation : [operation] } : {}),
	},
});

export class JuzPost implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'JuzPost',
		name: 'juzPost',
		icon: { light: 'file:juzpost.svg', dark: 'file:juzpost.dark.svg' },
		group: ['output'],
		version: 1,
		subtitle: '={{$parameter["operation"] + ": " + $parameter["resource"]}}',
		description:
			'Schedule and publish social media posts to 11 platforms from one calendar with JuzPost',
		defaults: { name: 'JuzPost' },
		usableAsTool: true,
		inputs: [NodeConnectionTypes.Main],
		outputs: [NodeConnectionTypes.Main],
		credentials: [{ name: 'juzPostApi', required: true }],
		properties: [
			{
				displayName: 'Resource',
				name: 'resource',
				type: 'options',
				noDataExpression: true,
				options: [
					{ name: 'Account', value: 'account' },
					{ name: 'Channel Group', value: 'group' },
					{ name: 'Media', value: 'media' },
					{ name: 'Post', value: 'post' },
					{ name: 'Workspace', value: 'workspace' },
				],
				default: 'post',
			},

			// ───────────────────────────── Post
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				displayOptions: show('post'),
				options: [
					{ name: 'Create Draft', value: 'create', action: 'Create a draft post', description: 'Create a post in draft status' },
					{ name: 'Delete Draft', value: 'delete', action: 'Delete a draft post', description: 'Delete a post that is still a draft' },
					{ name: 'Get', value: 'get', action: 'Get a post', description: 'Get one post with its per-account delivery state' },
					{ name: 'Get Many', value: 'getAll', action: 'Get many posts', description: 'List posts, newest first' },
					{ name: 'Schedule', value: 'schedule', action: 'Schedule a post', description: 'Send a draft to up to ten accounts, or publish it now' },
					{ name: 'Smart Schedule', value: 'smartSchedule', action: 'Smart schedule posts', description: 'Spread drafts across the workspace posting times' },
					{ name: 'Update Draft', value: 'update', action: 'Update a draft post', description: 'Edit a post that is still a draft' },
				],
				default: 'create',
			},
			{
				displayName: 'Post ID',
				name: 'postId',
				type: 'string',
				required: true,
				default: '',
				displayOptions: show('post', ['get', 'update', 'delete', 'schedule']),
			},
			{
				displayName: 'Content',
				name: 'content',
				type: 'string',
				typeOptions: { rows: 4 },
				default: '',
				description: 'The caption or body, up to 2200 characters',
				displayOptions: show('post', ['create', 'update']),
			},
			{
				displayName: 'Post Type',
				name: 'type',
				type: 'options',
				options: [
					{ name: 'Blog (WordPress)', value: 'blog' },
					{ name: 'Image', value: 'image' },
					{ name: 'Story', value: 'story' },
					{ name: 'Text', value: 'text' },
					{ name: 'Video', value: 'video' },
				],
				default: 'text',
				description:
					'Anything other than Text and Blog needs at least one media key before it can be scheduled',
				displayOptions: show('post', ['create']),
			},
			{
				displayName: 'Media Keys',
				name: 'mediaKeys',
				type: 'string',
				default: '',
				description: 'Comma-separated media keys returned by Media, Upload, in publish order',
				displayOptions: show('post', ['create', 'update']),
			},
			{
				displayName: 'Additional Fields',
				name: 'additionalFields',
				type: 'collection',
				placeholder: 'Add Field',
				default: {},
				displayOptions: show('post', ['create', 'update']),
				options: [
					{ displayName: 'Cover Image Key', name: 'coverR2Key', type: 'string', default: '' },
					{ displayName: 'Description', name: 'description', type: 'string', typeOptions: { rows: 3 }, default: '' },
					{ displayName: 'Hashtags', name: 'hashtags', type: 'string', default: '', description: 'Comma-separated, without the # prefix' },
					{ displayName: 'Post Type', name: 'type', type: 'options', options: [
						{ name: 'Blog (WordPress)', value: 'blog' }, { name: 'Image', value: 'image' }, { name: 'Story', value: 'story' }, { name: 'Text', value: 'text' }, { name: 'Video', value: 'video' },
					], default: 'text', displayOptions: { show: { '/operation': ['update'] } } },
					{ displayName: 'Title', name: 'title', type: 'string', default: '', description: 'Keep it under 100 characters if the post will be scheduled' },
				],
			},
			// schedule
			{
				displayName: 'Social Account Names or IDs',
				name: 'socialAccountIds',
				type: 'multiOptions',
				typeOptions: { loadOptionsMethod: 'getAccounts' },
				required: true,
				default: [],
				description:
					'Between one and ten accounts. Choose from the list, or specify IDs using an <a href="https://docs.n8n.io/code/expressions/">expression</a>.',
				displayOptions: show('post', ['schedule']),
			},
			{
				displayName: 'Publish At',
				name: 'publishAt',
				type: 'dateTime',
				default: '',
				description:
					'At least 10 minutes and at most about 6 months ahead. Leave empty to publish now.',
				displayOptions: show('post', ['schedule']),
			},
			{
				displayName: 'Overrides',
				name: 'overrides',
				type: 'collection',
				placeholder: 'Add Override',
				default: {},
				displayOptions: show('post', ['schedule']),
				options: [
					{ displayName: 'Description', name: 'description', type: 'string', typeOptions: { rows: 3 }, default: '' },
					{ displayName: 'Hashtags', name: 'hashtags', type: 'string', default: '', description: 'Comma-separated, without the # prefix' },
					{ displayName: 'Title', name: 'title', type: 'string', default: '', description: 'Up to 100 characters' },
				],
			},
			// smart schedule
			{
				displayName: 'Posts Per Day',
				name: 'minPerDay',
				type: 'number',
				typeOptions: { minValue: 1, maxValue: 20 },
				default: 1,
				required: true,
				displayOptions: show('post', ['smartSchedule']),
			},
			{
				displayName: 'Target',
				name: 'target',
				type: 'options',
				options: [
					{ name: 'Channel Group', value: 'group' },
					{ name: 'Accounts', value: 'accounts' },
				],
				default: 'group',
				displayOptions: show('post', ['smartSchedule']),
			},
			{
				displayName: 'Channel Group Name or ID',
				name: 'group',
				type: 'options',
				typeOptions: { loadOptionsMethod: 'getGroupNames' },
				default: '',
				description: 'Choose from the list, or specify a name using an <a href="https://docs.n8n.io/code/expressions/">expression</a>. Choose from the list, or specify an ID using an <a href="https://docs.n8n.io/code/expressions/">expression</a>.',
				displayOptions: { show: { resource: ['post'], operation: ['smartSchedule'], target: ['group'] } },
			},
			{
				displayName: 'Social Account Names or IDs',
				name: 'smartAccountIds',
				type: 'multiOptions',
				typeOptions: { loadOptionsMethod: 'getAccounts' },
				default: [],
				description:
					'Choose from the list, or specify IDs using an <a href="https://docs.n8n.io/code/expressions/">expression</a>',
				displayOptions: { show: { resource: ['post'], operation: ['smartSchedule'], target: ['accounts'] } },
			},
			{
				displayName: 'Options',
				name: 'smartOptions',
				type: 'collection',
				placeholder: 'Add Option',
				default: {},
				displayOptions: show('post', ['smartSchedule']),
				options: [
					{ displayName: 'Dry Run', name: 'dryRun', type: 'boolean', default: false, description: 'Whether to return the plan without creating any timers' },
					{ displayName: 'Post IDs', name: 'postIds', type: 'string', default: '', description: 'Comma-separated drafts to place, in order. Empty means every draft, oldest first.' },
					{ displayName: 'Posting Times', name: 'times', type: 'string', default: '', description: 'Comma-separated HH:MM times in the workspace timezone, overriding the defaults' },
					{ displayName: 'Start Date', name: 'startDate', type: 'string', default: '', placeholder: 'YYYY-MM-DD', description: 'First day to place posts on. Defaults to tomorrow.' },
				],
			},
			// get many posts
			{
				displayName: 'Return All',
				name: 'returnAll',
				type: 'boolean',
				default: false,
				description: 'Whether to return all results or only up to a given limit',
				displayOptions: { show: { resource: ['post', 'account', 'group'], operation: ['getAll'] } },
			},
			{
				displayName: 'Limit',
				name: 'limit',
				type: 'number',
				typeOptions: { minValue: 1 },
				default: 50,
				description: 'Max number of results to return',
				displayOptions: { show: { resource: ['post', 'account', 'group'], operation: ['getAll'], returnAll: [false] } },
			},
			{
				displayName: 'Filters',
				name: 'postFilters',
				type: 'collection',
				placeholder: 'Add Filter',
				default: {},
				displayOptions: show('post', ['getAll']),
				options: [
					{ displayName: 'Account Name or ID', name: 'accountId', type: 'options', typeOptions: { loadOptionsMethod: 'getAccounts' }, default: '', description: 'Choose from the list, or specify an ID using an <a href="https://docs.n8n.io/code/expressions/">expression</a>' },
					{ displayName: 'Created After', name: 'from', type: 'dateTime', default: '' },
					{ displayName: 'Created Before', name: 'to', type: 'dateTime', default: '' },
					{ displayName: 'Order', name: 'order', type: 'options', options: [{ name: 'Descending', value: 'desc' }, { name: 'Ascending', value: 'asc' }], default: 'desc' },
					{ displayName: 'Sort By', name: 'sort', type: 'options', options: [{ name: 'Created At', value: 'createdAt' }, { name: 'Scheduled For', value: 'scheduledFor' }], default: 'createdAt' },
					{ displayName: 'Status', name: 'status', type: 'options', options: [{ name: 'Draft', value: 'draft' }, { name: 'Failed', value: 'failed' }, { name: 'Posted', value: 'posted' }, { name: 'Scheduled', value: 'scheduled' }], default: 'draft' },
				],
			},

			// ───────────────────────────── Account
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				displayOptions: show('account'),
				options: [
					{ name: 'Get Many', value: 'getAll', action: 'Get many connected accounts', description: 'List the connected social accounts' },
				],
				default: 'getAll',
			},
			{
				displayName: 'Filters',
				name: 'accountFilters',
				type: 'collection',
				placeholder: 'Add Filter',
				default: {},
				displayOptions: show('account', ['getAll']),
				options: [
					{ displayName: 'Channel Group Name or ID', name: 'groupId', type: 'options', typeOptions: { loadOptionsMethod: 'getGroups' }, default: '', description: 'Choose from the list, or specify an ID using an <a href="https://docs.n8n.io/code/expressions/">expression</a>' },
					{ displayName: 'Platform', name: 'platform', type: 'options', options: PLATFORMS.map((p) => ({ name: p === 'x' ? 'X' : p[0].toUpperCase() + p.slice(1), value: p })), default: 'instagram' },
				],
			},

			// ───────────────────────────── Group
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				displayOptions: show('group'),
				options: [
					{ name: 'Get', value: 'get', action: 'Get a channel group', description: 'Get one group with its account IDs' },
					{ name: 'Get Many', value: 'getAll', action: 'Get many channel groups', description: 'List the channel groups' },
				],
				default: 'getAll',
			},
			{
				displayName: 'Channel Group Name or ID',
				name: 'groupId',
				type: 'options',
				typeOptions: { loadOptionsMethod: 'getGroups' },
				required: true,
				default: '',
				description:
					'Choose from the list, or specify an ID using an <a href="https://docs.n8n.io/code/expressions/">expression</a>',
				displayOptions: show('group', ['get']),
			},

			// ───────────────────────────── Media
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				displayOptions: show('media'),
				options: [
					{ name: 'Upload', value: 'upload', action: 'Upload a media file', description: 'Upload an image or video and get a media key for Create Draft' },
				],
				default: 'upload',
			},
			{
				displayName: 'Input Binary Field',
				name: 'binaryPropertyName',
				type: 'string',
				default: 'data',
				required: true,
				description: 'Name of the binary property that holds the file',
				displayOptions: show('media', ['upload']),
			},
			{
				displayName: 'File Name',
				name: 'fileName',
				type: 'string',
				default: '',
				description: 'Letters, digits, dot, underscore and dash. Defaults to the binary file name.',
				displayOptions: show('media', ['upload']),
			},

			// ───────────────────────────── Workspace
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				displayOptions: show('workspace'),
				options: [
					{ name: 'Get My Account', value: 'me', action: 'Get my account', description: 'User, workspace, plan, entitlements, quotas and blocked reasons' },
					{ name: 'Get Workspace', value: 'get', action: 'Get the workspace', description: 'Timezone and default posting times' },
				],
				default: 'me',
			},
		],
	};

	methods = {
		loadOptions: {
			async getAccounts(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
				const rows = await juzPostApiRequestAllItems.call(this, '/accounts', { sort: 'platform', order: 'asc' });
				return rows.map((a) => ({
					name: `${a.platform} · ${a.username}${a.isActive ? '' : ' (needs reconnect)'}`,
					value: a.id as string,
				}));
			},
			async getGroups(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
				const rows = await juzPostApiRequestAllItems.call(this, '/groups', { sort: 'name', order: 'asc' });
				return rows.map((g) => ({ name: `${g.name} (${g.accountCount} accounts)`, value: g.id as string }));
			},
			async getGroupNames(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
				const rows = await juzPostApiRequestAllItems.call(this, '/groups', { sort: 'name', order: 'asc' });
				return rows.map((g) => ({ name: `${g.name} (${g.accountCount} accounts)`, value: g.name as string }));
			},
		},
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];
		const resource = this.getNodeParameter('resource', 0) as string;
		const operation = this.getNodeParameter('operation', 0) as string;

		for (let i = 0; i < items.length; i++) {
			try {
				let result: IDataObject | IDataObject[];

				if (resource === 'workspace') {
					result = await juzPostApiRequest.call(this, 'GET', operation === 'me' ? '/me' : '/workspace');
				} else if (resource === 'account') {
					const filters = this.getNodeParameter('accountFilters', i, {}) as IDataObject;
					result = await listAll.call(this, i, '/accounts', clean(filters));
				} else if (resource === 'group') {
					if (operation === 'get') {
						const groupId = this.getNodeParameter('groupId', i) as string;
						result = await juzPostApiRequest.call(this, 'GET', `/groups/${encodeURIComponent(groupId)}`);
					} else {
						result = await listAll.call(this, i, '/groups', {});
					}
				} else if (resource === 'media') {
					result = await uploadMedia.call(this, i);
				} else if (resource === 'post') {
					result = await postOperation.call(this, i, operation);
				} else {
					throw new NodeOperationError(this.getNode(), `Unknown resource ${resource}`, { itemIndex: i });
				}

				const rows = Array.isArray(result) ? result : [result];
				for (const row of rows) returnData.push({ json: row, pairedItem: { item: i } });
			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({ json: { error: (error as Error).message }, pairedItem: { item: i } });
					continue;
				}
				throw new NodeOperationError(this.getNode(), error as Error, { itemIndex: i });
			}
		}
		return [returnData];
	}
}

async function listAll(this: IExecuteFunctions, i: number, endpoint: string, qs: IDataObject) {
	const returnAll = this.getNodeParameter('returnAll', i, false) as boolean;
	const limit = returnAll ? 0 : (this.getNodeParameter('limit', i, 50) as number);
	return juzPostApiRequestAllItems.call(this, endpoint, qs, limit);
}

async function uploadMedia(this: IExecuteFunctions, i: number): Promise<IDataObject> {
	const binaryPropertyName = this.getNodeParameter('binaryPropertyName', i) as string;
	const binary = this.helpers.assertBinaryData(i, binaryPropertyName);
	const buffer = await this.helpers.getBinaryDataBuffer(i, binaryPropertyName);
	const fileName = ((this.getNodeParameter('fileName', i, '') as string) || binary.fileName || 'upload.bin')
		.replace(/[^A-Za-z0-9._-]/g, '_');
	const contentType = binary.mimeType || 'application/octet-stream';

	const presign = await juzPostApiRequest.call(this, 'POST', '/storage/presign', {
		relativeKey: `media/${fileName}`,
		contentType,
		operation: 'upload',
		contentLength: buffer.length,
	});

	await this.helpers.httpRequest({
		method: 'PUT',
		url: presign.signedUrl as string,
		body: buffer,
		headers: { 'Content-Type': contentType },
	});

	return { mediaKey: presign.resolvedKey, fileName, contentType, contentLength: buffer.length };
}

async function postOperation(this: IExecuteFunctions, i: number, operation: string): Promise<IDataObject | IDataObject[]> {
	switch (operation) {
		case 'create':
		case 'update': {
			const extra = this.getNodeParameter('additionalFields', i, {}) as IDataObject;
			const body = clean({
				content: this.getNodeParameter('content', i, '') as string,
				type: operation === 'create' ? (this.getNodeParameter('type', i) as string) : extra.type,
				mediaUrls: csv(this.getNodeParameter('mediaKeys', i, '') as string),
				title: extra.title,
				description: extra.description,
				hashtags: csv(extra.hashtags as string),
				coverR2Key: extra.coverR2Key,
			});
			if (operation === 'create') return juzPostApiRequest.call(this, 'POST', '/posts', body);
			const postId = this.getNodeParameter('postId', i) as string;
			return juzPostApiRequest.call(this, 'PATCH', `/posts/${encodeURIComponent(postId)}`, body);
		}
		case 'get': {
			const postId = this.getNodeParameter('postId', i) as string;
			return juzPostApiRequest.call(this, 'GET', `/posts/${encodeURIComponent(postId)}`);
		}
		case 'delete': {
			const postId = this.getNodeParameter('postId', i) as string;
			return juzPostApiRequest.call(this, 'DELETE', `/posts/${encodeURIComponent(postId)}`);
		}
		case 'getAll': {
			const filters = this.getNodeParameter('postFilters', i, {}) as IDataObject;
			return listAll.call(this, i, '/posts', clean(filters));
		}
		case 'schedule': {
			const postId = this.getNodeParameter('postId', i) as string;
			const overrides = this.getNodeParameter('overrides', i, {}) as IDataObject;
			const publishAt = this.getNodeParameter('publishAt', i, '') as string;
			const body = clean({
				socialAccountIds: csv(this.getNodeParameter('socialAccountIds', i) as string[]),
				publishAt: publishAt ? new Date(publishAt).toISOString() : undefined,
				title: overrides.title,
				description: overrides.description,
				hashtags: csv(overrides.hashtags as string),
			});
			return juzPostApiRequest.call(this, 'POST', `/posts/${encodeURIComponent(postId)}/schedule`, body);
		}
		case 'smartSchedule': {
			const target = this.getNodeParameter('target', i) as string;
			const opts = this.getNodeParameter('smartOptions', i, {}) as IDataObject;
			const body = clean({
				minPerDay: this.getNodeParameter('minPerDay', i) as number,
				group: target === 'group' ? (this.getNodeParameter('group', i) as string) : undefined,
				socialAccountIds: target === 'accounts' ? csv(this.getNodeParameter('smartAccountIds', i) as string[]) : undefined,
				postIds: csv(opts.postIds as string),
				times: csv(opts.times as string),
				startDate: opts.startDate,
				dryRun: opts.dryRun === true ? true : undefined,
			});
			return juzPostApiRequest.call(this, 'POST', '/schedule', body);
		}
		default:
			throw new NodeOperationError(this.getNode(), `Unknown operation ${operation}`, { itemIndex: i });
	}
}
