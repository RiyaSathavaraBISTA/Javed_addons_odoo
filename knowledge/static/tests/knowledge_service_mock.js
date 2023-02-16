/** @odoo-module */

import { patch } from '@web/core/utils/patch';
import { registry } from '@web/core/registry';
import { utils } from '@web/../tests/helpers/mock_env';

const { prepareRegistriesWithCleanup } = utils;

export function makeFakeMessagingServiceForKnowledge() {
    return {
        start() {
            return {
                async get() {
                    return {
                        knowledge: {
                            update() {},
                        },
                        messagingBus: {
                            addEventListener() {},
                            removeEventListener() {},
                            trigger() {},
                        },
                        openChat() {},
                        rpc() {},
                    };
                },
                modelManager: {
                    startListening() {},
                    stopListening() {},
                    removeListener() {},
                    messagingCreatedPromise: Promise.resolve(),
                },
            };
        }
    };
}

function makeFakeKnowledgeService() {
    return {
        start() {
            return {
                registerRecord() {},
                unregisterRecord() {},
                getAvailableRecordWithChatter() {
                    return null;
                },
                getAvailableRecordWithHtmlField() {
                    return null;
                },
                getRecords() {
                    return new Set();
                },
            };
        }
    };
}

const serviceRegistry = registry.category('services');
patch(utils, 'knowledge_test_registries', {
    prepareRegistriesWithCleanup() {
        prepareRegistriesWithCleanup(...arguments);
        serviceRegistry.add('knowledgeService', makeFakeKnowledgeService());
    },
});
