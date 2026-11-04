import type {
	IAuthenticateGeneric,
	ICredentialTestRequest,
	ICredentialType,
	Icon,
	INodeProperties,
} from 'n8n-workflow';

export class JuzPostApi implements ICredentialType {
	name = 'juzPostApi';

	displayName = 'JuzPost API';

	icon: Icon = { light: 'file:../nodes/JuzPost/juzpost.svg', dark: 'file:../nodes/JuzPost/juzpost.dark.svg' };

	documentationUrl = 'https://api.juzpost.com/docs';

	properties: INodeProperties[] = [
		{
			displayName: 'API Key',
			name: 'apiKey',
			type: 'string',
			typeOptions: { password: true },
			default: '',
			description:
				'In JuzPost open Settings, General, then the API keys card and choose Generate API key. The key starts with jp_live_ and is shown once.',
		},
	];

	authenticate: IAuthenticateGeneric = {
		type: 'generic',
		properties: {
			headers: {
				Authorization: '=Bearer {{$credentials.apiKey}}',
			},
		},
	};

	test: ICredentialTestRequest = {
		request: {
			baseURL: 'https://www.juzpost.com/api/cli/v1',
			url: '/me',
			method: 'GET',
		},
	};
}
