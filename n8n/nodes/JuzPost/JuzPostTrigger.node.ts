import type {
	IDataObject,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	IPollFunctions,
} from 'n8n-workflow';
import { NodeConnectionTypes } from 'n8n-workflow';

import { juzPostApiRequestAllItems } from './GenericFunctions';

interface PollData {
	seen?: Record<string, string>;
}

export class JuzPostTrigger implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'JuzPost Trigger',
		name: 'juzPostTrigger',
		icon: { light: 'file:juzpost.svg', dark: 'file:juzpost.dark.svg' },
		group: ['trigger'],
		version: 1,
		subtitle: '={{"Posts: " + $parameter["status"]}}',
		description: 'Starts the workflow when a JuzPost post reaches a status, for example posted or failed',
		defaults: { name: 'JuzPost Trigger' },
		polling: true,
		inputs: [],
		outputs: [NodeConnectionTypes.Main],
		credentials: [{ name: 'juzPostApi', required: true }],
		properties: [
			{
				displayName: 'Status',
				name: 'status',
				type: 'options',
				options: [
					{ name: 'Draft', value: 'draft' },
					{ name: 'Failed', value: 'failed' },
					{ name: 'Posted', value: 'posted' },
					{ name: 'Scheduled', value: 'scheduled' },
				],
				default: 'posted',
				description: 'Emit a post once each time it reaches this status',
			},
			{
				displayName: 'Limit',
				name: 'limit',
				type: 'number',
				typeOptions: { minValue: 1, maxValue: 100 },
				default: 50,
				description: 'Max number of results to return',
			},
		],
	};

	async poll(this: IPollFunctions): Promise<INodeExecutionData[][] | null> {
		const status = this.getNodeParameter('status') as string;
		const limit = this.getNodeParameter('limit') as number;
		const pollData = this.getWorkflowStaticData('node') as PollData;
		const seen = pollData.seen ?? {};

		const rows = (await juzPostApiRequestAllItems.call(
			this,
			'/posts',
			{ status, sort: 'createdAt', order: 'desc' },
			limit,
		)) as IDataObject[];

		if (this.getMode() === 'manual') {
			return rows.length ? [this.helpers.returnJsonArray(rows.slice(0, 1))] : null;
		}

		const fresh = rows.filter((r) => seen[r.id as string] !== (r.updatedAt as string));
		for (const r of rows) seen[r.id as string] = r.updatedAt as string;
		// Keep the memory bounded: forget ids no longer in the latest page.
		const keep = new Set(rows.map((r) => r.id as string));
		pollData.seen = Object.fromEntries(Object.entries(seen).filter(([id]) => keep.has(id)));

		return fresh.length ? [this.helpers.returnJsonArray(fresh)] : null;
	}
}
