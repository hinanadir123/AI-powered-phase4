# Phase 5 Test Suite - Quick Start Guide

**Version:** 1.0
**Date:** 2026-02-15

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Install Playwright browsers (for E2E tests)
playwright install
```

### 2. Start Services

```bash
# Option A: Using Docker Compose
docker-compose up -d

# Option B: Using Dapr CLI
dapr run --app-id backend --app-port 8000 -- python backend/main.py
dapr run --app-id worker --app-port 5001 -- python worker/main.py
```

### 3. Run Tests

```bash
# Run all tests
./tests/run_tests.sh all

# Run integration tests only (faster)
./tests/run_tests.sh integration

# Run smoke tests (quickest validation)
./tests/run_tests.sh smoke
```

### 4. View Results

```bash
# Open HTML report
open tests/reports/full-report.html

# View coverage
open tests/coverage/html/index.html
```

---

## 📋 Common Commands

### Run Specific Test Categories

```bash
# Kafka/Dapr Pub/Sub tests
./tests/run_tests.sh kafka

# Dapr Jobs API tests
./tests/run_tests.sh jobs

# Dapr State Store tests
./tests/run_tests.sh state

# E2E tests
./tests/run_tests.sh e2e
```

### Run Individual Test Files

```bash
# Single test file
pytest tests/integration/test_kafka_dapr_pubsub.py -v

# Single test function
pytest tests/integration/test_kafka_dapr_pubsub.py::TestKafkaDaprPubSub::test_publish_task_created_event -v

# With coverage
pytest tests/integration/test_kafka_dapr_pubsub.py --cov=agents/backend --cov-report=html
```

### Debug Tests

```bash
# Run with verbose output
pytest tests/integration -vv

# Show print statements
pytest tests/integration -s

# Stop on first failure
pytest tests/integration -x

# Run last failed tests
pytest tests/integration --lf

# Run with debugger
pytest tests/integration --pdb
```

---

## ✅ Pre-Test Checklist

Before running tests, ensure:

- [ ] Backend API running on port 8000
- [ ] Reminder Worker running on port 5001
- [ ] Dapr sidecar running on port 3500
- [ ] Kafka cluster accessible
- [ ] PostgreSQL database accessible
- [ ] Frontend running on port 3000 (for E2E tests)

**Quick Health Check:**
```bash
curl http://localhost:8000/health
curl http://localhost:5001/health
curl http://localhost:3500/v1.0/healthz
```

---

## 🐛 Troubleshooting

### Services Not Running

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs backend
docker-compose logs worker

# Restart services
docker-compose restart
```

### Dapr Issues

```bash
# Check Dapr status
dapr status -k

# Verify components
dapr components -k

# Check Dapr logs
kubectl logs -l app=dapr-sidecar-injector -n dapr-system
```

### Test Failures

```bash
# Run with more verbose output
pytest tests/integration -vv -s

# Check test logs
cat tests/logs/pytest.log

# Run single failing test
pytest tests/integration/test_kafka_dapr_pubsub.py::test_name -vv
```

---

## 📊 Test Coverage Goals

- **Integration Tests:** > 90%
- **E2E Tests:** > 95%
- **Overall:** > 92%

**Check Coverage:**
```bash
pytest tests/integration --cov=agents/backend --cov-report=term-missing
```

---

## 🔄 CI/CD Integration

Tests run automatically on:
- Push to `main` branch
- Pull requests to `main`
- Manual workflow dispatch

**View CI/CD Status:**
```bash
gh run list --workflow=deploy.yml
```

---

## 📚 Documentation

- **Full Documentation:** `tests/README.md`
- **Deployment Testing:** `agents/deployment-tester-agent.md`
- **Phase 5 Spec:** `phase5-spec.md`
- **Task Breakdown:** `phase5-tasks.md`

---

## 🎯 Success Criteria

Tests are passing when:
- ✅ All 62 tests pass (37 integration + 25 E2E)
- ✅ Code coverage > 92%
- ✅ No errors in service logs
- ✅ All Dapr components loaded
- ✅ Kafka events flowing correctly

---

## 💡 Tips

1. **Run integration tests first** - They're faster and catch most issues
2. **Use smoke tests** for quick validation during development
3. **Run E2E tests in headed mode** to see browser interactions: `pytest tests/e2e --headed`
4. **Check logs** if tests fail - they contain detailed error information
5. **Clean up test data** - Tests should clean up after themselves, but verify manually if needed

---

## 🆘 Need Help?

1. Check `tests/README.md` for detailed documentation
2. Review test logs in `tests/logs/pytest.log`
3. Check service logs: `docker-compose logs`
4. Verify Dapr components: `dapr components -k`
5. Test individual components: `curl http://localhost:3500/v1.0/healthz`

---

**Happy Testing! 🎉**
