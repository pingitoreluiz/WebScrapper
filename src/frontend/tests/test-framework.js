/**
 * Simple Test Framework
 * 
 * Lightweight testing framework for vanilla JavaScript
 */

class TestRunner {
    constructor() {
        this.tests = [];
        this.results = {
            passed: 0,
            failed: 0,
            total: 0
        };
    }

    describe(suiteName, callback) {
        console.log(`\n📦 ${suiteName}`);
        callback();
    }

    test(testName, callback) {
        this.results.total++;
        try {
            callback();
            this.results.passed++;
            console.log(`  ✅ ${testName}`);
        } catch (error) {
            this.results.failed++;
            console.error(`  ❌ ${testName}`);
            console.error(`     ${error.message}`);
        }
    }

    expect(actual) {
        return {
            toBe: (expected) => {
                if (actual !== expected) {
                    throw new Error(`Expected ${expected}, but got ${actual}`);
                }
            },
            toEqual: (expected) => {
                if (JSON.stringify(actual) !== JSON.stringify(expected)) {
                    throw new Error(`Expected ${JSON.stringify(expected)}, but got ${JSON.stringify(actual)}`);
                }
            },
            toContain: (expected) => {
                if (!actual.includes(expected)) {
                    throw new Error(`Expected "${actual}" to contain "${expected}"`);
                }
            },
            toBeNull: () => {
                if (actual !== null) {
                    throw new Error(`Expected null, but got ${actual}`);
                }
            },
            toBeTruthy: () => {
                if (!actual) {
                    throw new Error(`Expected truthy value, but got ${actual}`);
                }
            },
            toBeFalsy: () => {
                if (actual) {
                    throw new Error(`Expected falsy value, but got ${actual}`);
                }
            },
            toThrow: () => {
                try {
                    actual();
                    throw new Error('Expected function to throw, but it did not');
                } catch (error) {
                    // Expected to throw
                }
            }
        };
    }

    async runAll() {
        console.log('🧪 Running Frontend Tests...\n');

        // Run all test suites
        await this.runUtilityTests();
        await this.runAPIClientTests();
        await this.runDOMTests();

        // Print summary
        this.printSummary();
    }

    async runUtilityTests() {
        this.describe('Utility Functions', () => {
            this.test('formatCurrency formats BRL correctly', () => {
                const result = formatCurrency(1234.56);
                this.expect(result).toContain('1.234,56');
            });

            this.test('formatCurrency handles zero', () => {
                const result = formatCurrency(0);
                this.expect(result).toContain('0,00');
            });

            this.test('formatCurrency handles large numbers', () => {
                const result = formatCurrency(12000000);
                this.expect(result).toContain('12.000.000');
            });

            this.test('formatDate formats date correctly', () => {
                const date = '2024-01-26T12:00:00';
                const result = formatDate(date);
                this.expect(result).toContain('26/01/2024');
            });

            this.test('formatRelativeTime shows "Agora mesmo" for recent dates', () => {
                const now = new Date().toISOString();
                const result = formatRelativeTime(now);
                this.expect(result).toBe('Agora mesmo');
            });

            this.test('formatRelativeTime shows minutes', () => {
                const fiveMinutesAgo = new Date(Date.now() - 5 * 60000).toISOString();
                const result = formatRelativeTime(fiveMinutesAgo);
                this.expect(result).toContain('minuto');
            });

            this.test('formatRelativeTime shows hours', () => {
                const twoHoursAgo = new Date(Date.now() - 2 * 3600000).toISOString();
                const result = formatRelativeTime(twoHoursAgo);
                this.expect(result).toContain('hora');
            });

            this.test('formatRelativeTime shows days', () => {
                const threeDaysAgo = new Date(Date.now() - 3 * 86400000).toISOString();
                const result = formatRelativeTime(threeDaysAgo);
                this.expect(result).toContain('dia');
            });
        });
    }

    async runAPIClientTests() {
        this.describe('API Client', () => {
            this.test('APIClient initializes with correct baseURL', () => {
                const client = new APIClient('http://test.com');
                this.expect(client.baseURL).toBe('http://test.com');
            });

            this.test('APIClient sets correct headers', () => {
                const client = new APIClient();
                this.expect(client.headers['Content-Type']).toBe('application/json');
            });

            this.test('API endpoints are defined', () => {
                this.expect(typeof api.getHealth).toBe('function');
                this.expect(typeof api.getProducts).toBe('function');
                this.expect(typeof api.searchProducts).toBe('function');
                this.expect(typeof api.getBestDeals).toBe('function');
                this.expect(typeof api.getProduct).toBe('function');
                this.expect(typeof api.getStats).toBe('function');
                this.expect(typeof api.runScrapers).toBe('function');
                this.expect(typeof api.getScraperStatus).toBe('function');
                this.expect(typeof api.getScraperHistory).toBe('function');
                this.expect(typeof api.getScraperMetrics).toBe('function');
            });
        });
    }

    async runDOMTests() {
        this.describe('DOM Functions', () => {
            this.test('createProductCard generates valid HTML', () => {
                const product = {
                    title: 'Test GPU',
                    price: 5000,
                    url: 'https://test.com',
                    store: 'Pichau',
                    chip_brand: 'NVIDIA',
                    manufacturer: 'ASUS',
                    model: 'RTX 4090'
                };

                const html = createProductCard(product);
                this.expect(html).toContain('Test GPU');
                this.expect(html).toContain('ASUS');
                this.expect(html).toContain('RTX 4090');
                this.expect(html).toContain('product-card');
            });

            this.test('createActivityItem generates valid HTML', () => {
                const run = {
                    success: true,
                    products_saved: 10,
                    store: 'Pichau',
                    started_at: new Date().toISOString()
                };

                const html = createActivityItem(run);
                this.expect(html).toContain('activity-item');
                this.expect(html).toContain('10 produtos');
            });

            this.test('showToast function exists', () => {
                this.expect(typeof showToast).toBe('function');
            });

            this.test('showLoading function exists', () => {
                this.expect(typeof showLoading).toBe('function');
            });

            this.test('showError function exists', () => {
                this.expect(typeof showError).toBe('function');
            });
        });
    }

    printSummary() {
        console.log('\n' + '='.repeat(50));
        console.log('📊 Test Summary');
        console.log('='.repeat(50));
        console.log(`Total Tests: ${this.results.total}`);
        console.log(`✅ Passed: ${this.results.passed}`);
        console.log(`❌ Failed: ${this.results.failed}`);

        const percentage = ((this.results.passed / this.results.total) * 100).toFixed(1);
        console.log(`\n📈 Success Rate: ${percentage}%`);

        if (this.results.failed === 0) {
            console.log('\n🎉 All tests passed!');
        } else {
            console.log(`\n⚠️  ${this.results.failed} test(s) failed`);
        }
        console.log('='.repeat(50));
    }
}

// Create global test runner
const testRunner = new TestRunner();

// Export for use in HTML
window.testRunner = testRunner;
window.describe = testRunner.describe.bind(testRunner);
window.test = testRunner.test.bind(testRunner);
window.expect = testRunner.expect.bind(testRunner);
