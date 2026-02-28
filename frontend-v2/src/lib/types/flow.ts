export type FlowIntent = 'whatsapp' | 'artikel' | 'aantekening';

export type ClassifyResult = {
	intent: FlowIntent;
	params: Record<string, string>;
	confidence: number;
};

export type FlowExecution = {
	execution_id: string;
	status: 'pending' | 'running' | 'success' | 'error';
	message: string;
};

export type FlowStatus = {
	execution_id: string;
	status: 'pending' | 'running' | 'success' | 'error';
	result: Record<string, unknown> | null;
	error: string | null;
};
