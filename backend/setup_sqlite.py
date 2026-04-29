# setup_sqlite.py
import sqlite3

def setup_database():
    """Create runbooks table and insert sample data"""
    
    print("Creating SQLite database...")
    conn = sqlite3.connect('runbooks.db')
    cursor = conn.cursor()
    
    # Create runbooks table
    print("Creating runbooks table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            keywords TEXT NOT NULL,
            steps TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if runbooks already exist
    cursor.execute("SELECT COUNT(*) FROM runbooks")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Table already has {count} runbooks. Clearing and reinserting...")
        cursor.execute("DELETE FROM runbooks")
    
    # Insert 5 detailed runbooks
    print("Inserting sample runbooks...")
    
    runbooks = [
        (
            "Database Connection Failure",
            "database",
            "database,connection,timeout,postgres,mysql,db,cannot connect,connection refused,database down",
            """1. Check database service status
Command: systemctl status postgresql
Expected: Service should be 'active (running)'
Action: If inactive, proceed to restart

2. Verify database process is running
Command: ps aux | grep postgres
Expected: Should see multiple postgres processes
Action: If no processes, database service is down

3. Test database connectivity from localhost
Command: psql -h localhost -U postgres -d your_database
Replace: your_database with actual database name
Expected: Should connect without timeout
If fails: Database service issue or wrong credentials

4. Test database connectivity from application server
Command: telnet db.example.com 5432
Replace: db.example.com with actual hostname
Expected: Connection should succeed
If fails: Network/firewall issue

5. Review database logs for errors
Command: tail -f /var/log/postgresql/postgresql-14-main.log
Look for: Connection errors, authentication failures, crash messages
Common errors: "too many connections", "out of memory"

6. Check database connection limits
Command: psql -c "SHOW max_connections;"
Action: If application hitting limit, increase max_connections
File: /etc/postgresql/14/main/postgresql.conf

7. Verify connection pool settings in application
File: application.properties or config.py
Check: 
- DATABASE_URL is correct
- Connection pool size (max 20-50 for most apps)
- Connection timeout (30-60 seconds recommended)

8. Check for connection leaks in application
Command: psql -c "SELECT count(*) FROM pg_stat_activity;"
Action: If count near max_connections, application not closing connections
Fix: Review application code for proper connection handling

9. Restart database service if needed
Command: sudo systemctl restart postgresql
Warning: This disconnects all current connections
Expected: Service should restart within 10-30 seconds

10. Test application connection after restart
Command: curl http://localhost:8080/health
Expected: Application should reconnect automatically
If fails: Check application logs

11. Verify firewall rules
Command: sudo iptables -L -n | grep 5432
Expected: Port 5432 should be open for application server IP
Action: Add rule if missing

12. Check DNS resolution
Command: nslookup db.example.com
Expected: Should resolve to correct IP
If fails: DNS configuration issue"""
        ),
        (
            "High CPU Usage",
            "performance",
            "cpu,high usage,performance,slow,resource,100% cpu,high load,server slow,application slow",
            """1. Check current CPU usage overview
Command: top -b -n 1 | head -20
Look for: Processes with high %CPU (>80%)
Note: PID and process names of top consumers

2. Identify top CPU-consuming processes
Command: ps aux --sort=-%cpu | head -10
Action: Document PIDs of top 3 processes
Check: Are these expected processes?

3. Check system load average
Command: uptime
Expected: Load average should be below number of CPU cores
Example: 4-core system should have load < 4.0
If higher: System is significantly overloaded

4. Monitor specific process in real-time
Command: top -p <PID>
Replace: <PID> with problematic process ID
Monitor: CPU usage over 2-3 minutes
Action: If consistently high, investigate further

5. Check for runaway processes or infinite loops
Command: ps -eo pid,ppid,cmd,%cpu,time --sort=-%cpu | head -20
Look for: Processes with excessive TIME (hours of CPU time)
Action: These are likely stuck in loops

6. Review application logs for errors
Command: tail -f /var/log/application/app.log
Look for: 
- Repeated error messages
- Stack traces
- Database timeout errors
- Memory allocation failures

7. Check for CPU-intensive scheduled jobs
Command: crontab -l
Action: Check if any cron jobs running during high CPU period
Temporary fix: Comment out non-critical jobs

8. Analyze process thread count
Command: ps -eLf | grep <process_name>
Expected: Reasonable thread count (usually < 200 for web apps)
If excessive: Possible thread leak in application

9. Check for zombie processes
Command: ps aux | grep 'Z'
Action: If found, identify parent process and restart it
Zombie processes don't use CPU but indicate issues

10. Review recent code deployments
Action: Check if CPU spike started after recent deployment
If yes: Consider rollback while investigating
Command: git log --since="2 days ago"

11. Kill problematic process (if safe to do so)
Command: kill -15 <PID> (graceful shutdown)
Wait: 30 seconds
If not stopped: kill -9 <PID> (force kill)
Warning: Only kill after confirming process is safe to restart

12. Monitor CPU after mitigation
Command: watch -n 2 'top -b -n 1 | head -15'
Expected: CPU usage should decrease to normal levels
Normal: < 70% average for production systems

13. Check I/O wait time
Command: iostat -x 1 5
Look for: High %iowait (>20%)
If high: CPU waiting on disk, check disk performance

14. Review application performance metrics
Tool: Use APM tools (New Relic, DataDog) if available
Check: Request latency, throughput, error rates
Action: Identify slow endpoints or queries

15. Consider horizontal scaling
Short-term: Add more application instances
Long-term: Load balancer distribution
Cloud: Auto-scaling rules

16. Consider vertical scaling
Action: Increase CPU cores/resources
AWS: Change instance type
Azure: Scale up VM size

17. Enable CPU profiling for root cause analysis
Python: py-spy top --pid <PID>
Java: jstack <PID>
Node.js: node --prof app.js
Action: Identify hot code paths for optimization"""
        ),
        (
            "Disk Space Full",
            "storage",
            "disk,storage,space,full,no space,disk full,100% disk,out of space,cannot write",
            """1. Check disk usage overview
Command: df -h
Look for: Filesystems with >90% usage
Critical: Any at 100%
Note: Which filesystem is full (/var, /home, /)

2. Identify largest directories (root level)
Command: du -sh /* 2>/dev/null | sort -rh | head -10
Warning: This may take 1-2 minutes
Note: Top 3 largest directories

3. Check common problem areas
Command: du -sh /var/log /tmp /home /opt 2>/dev/null | sort -rh
Look for: Unexpectedly large directories (>5GB)
Common culprits: /var/log, /tmp

4. Find large files across system
Command: find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -20
Action: Review and delete if safe
Check: Are these log files, backups, or core dumps?

5. Check log file sizes in detail
Command: ls -lh /var/log/*.log | sort -k5 -rh | head -10
Look for: Files >500MB
Action: These need immediate attention

6. Analyze application log directory
Command: du -sh /var/log/application/* | sort -rh
Look for: Logs that should have been rotated
Check: Are log rotation rules working?

7. Clean up old rotated log files (safe)
Command: find /var/log -name "*.log.*" -mtime +30 -delete
Action: Delete logs older than 30 days
Warning: Adjust retention based on compliance requirements

8. Compress large current log files
Command: gzip /var/log/application/large-file.log
Benefit: Typically reduces size by 90%+
Note: Application must handle .gz files or be restarted

9. Truncate active log files (emergency only)
Command: > /var/log/application/app.log
Warning: This clears the log file
Use only: When disk is 100% full and other options exhausted

10. Check for core dumps
Command: find / -name "core.*" -type f 2>/dev/null
Size: Core dumps can be 1GB+ each
Action: Delete if not actively debugging

11. Clear package manager cache (Ubuntu/Debian)
Command: sudo apt-get clean
Location: /var/cache/apt/archives
Expected: Can free 500MB-2GB

12. Clear package manager cache (RedHat/CentOS)
Command: sudo yum clean all
Location: /var/cache/yum
Expected: Can free 500MB-1GB

13. Find and analyze duplicate files
Command: fdupes -r /home | head -50
Action: Review duplicates before deleting
Use case: User home directories with duplicate downloads

14. Check for old backup files
Command: find / -name "*.bak" -o -name "*.backup" 2>/dev/null | head -20
Action: Delete backups older than retention policy
Check: Are automated backups being cleaned up?

15. Remove old Docker images and containers
Command: docker system df
Shows: Space used by images, containers, volumes
Command: docker system prune -a
Warning: Removes ALL unused Docker data
Expected: Can free 5-20GB if Docker is used

16. Check database data directory size
PostgreSQL: du -sh /var/lib/postgresql/data
MySQL: du -sh /var/lib/mysql
Action: If large, consider:
- VACUUM (PostgreSQL)
- Archiving old data
- Purging old records

17. Vacuum PostgreSQL database (if applicable)
Command: psql -c "VACUUM FULL VERBOSE;"
Warning: Locks tables during operation
Expected: Can reclaim 10-30% space
Downtime: 5-30 minutes depending on DB size

18. Archive old application data
Action: Move old data to archival storage
Example: Records older than 1 year
Command: Custom SQL query or script
Benefit: Can free significant space

19. Set up log rotation (prevent future issues)
File: /etc/logrotate.d/application
Config:
  daily
  rotate 7
  compress
  delaycompress
  missingok
Test: logrotate -f /etc/logrotate.d/application

20. Configure application log limits
Update: application.properties
Set: max-file-size: 100MB, max-history: 30 days
Benefit: Prevents log files from growing uncontrolled

21. Set up disk usage monitoring
Tool: Prometheus + Grafana or CloudWatch
Alert: When disk usage >80%
Action: Receive notification before critical

22. Restart application if disk was at 100%
Reason: Application may have stopped due to write failures
Command: systemctl restart application
Check: Application logs for any corruption issues

23. Verify filesystem is not corrupt
Command: sudo fsck -n /dev/sda1
Replace: /dev/sda1 with actual device
Action: If errors found, run fsck in single-user mode

24. Check for large temporary files
Command: du -sh /tmp/* | sort -rh | head -10
Action: Delete old temp files (>1 day old)
Command: find /tmp -type f -mtime +1 -delete"""
        ),
        (
            "Application Deployment Failure",
            "deployment",
            "deployment,deploy,release,failed deployment,deployment error,build failed,pipeline failed,ci cd,jenkins,gitlab",
            """1. Check deployment pipeline status
Command: kubectl get pods -n production (Kubernetes)
Or: Check CI/CD dashboard (Jenkins/GitLab/GitHub Actions)
Expected: All pods running or build succeeded
Action: Note failed step/stage

2. Review deployment logs
Command: kubectl logs <pod-name> -n production
Or: Check pipeline logs in CI/CD tool
Look for: Error messages, stack traces, timeout errors
Common errors: Image pull errors, configuration issues

3. Verify Docker image exists
Command: docker pull <image-name>:<tag>
Expected: Image downloads successfully
If fails: Image not pushed to registry or wrong tag

4. Check image registry access
Command: docker login <registry-url>
Expected: Login successful
If fails: Credentials expired or wrong permissions

5. Verify application configuration
File: config.yaml or application.properties
Check:
- Environment variables are set correctly
- Database URLs are correct
- API keys and secrets are present
- Port configurations match

6. Check resource limits and quotas
Command: kubectl describe pod <pod-name>
Look for: OOMKilled, CPU throttling, insufficient resources
Action: Increase memory/CPU limits if needed

7. Verify network connectivity
Command: kubectl exec -it <pod-name> -- ping <service-name>
Expected: Connectivity to required services
If fails: Network policies or firewall blocking

8. Check database migrations
Command: Check migration logs or run manually
Expected: All migrations applied successfully
If fails: Fix migration scripts, rollback if needed

9. Verify health check endpoints
Command: curl http://<service-url>/health
Expected: 200 OK with healthy status
If fails: Application not starting properly

10. Review recent code changes
Command: git diff HEAD~1 HEAD
Action: Identify what changed in failed deployment
Consider: Rollback if critical bug introduced

11. Check environment-specific issues
Action: Compare staging vs production configs
Common: Database credentials, API endpoints differ
Verify: Environment variables in deployment manifest

12. Verify secrets and ConfigMaps
Command: kubectl get secrets,configmaps -n production
Expected: All required secrets exist
If missing: Create or update from secure storage

13. Check service dependencies
Action: Verify all dependent services are running
Examples: Database, Redis, message queue, external APIs
Command: kubectl get svc -n production

14. Review application startup time
Check: If application times out during health checks
Action: Increase initialDelaySeconds in liveness probe
Typical: 60-120 seconds for complex applications

15. Check for port conflicts
Command: netstat -tulpn | grep <port>
Expected: Port is available or correctly bound
If conflict: Change port or stop conflicting service

16. Verify SSL/TLS certificates
Command: openssl s_client -connect <host>:443
Expected: Valid certificate, not expired
If fails: Renew certificates or update cert-manager

17. Check storage volumes and persistence
Command: kubectl get pvc -n production
Expected: All PVCs bound and available
If fails: Storage class issues or insufficient storage

18. Review rollback strategy
Action: If deployment critically failed
Command: kubectl rollout undo deployment/<name>
Or: Revert to previous release in CI/CD pipeline

19. Test in staging environment first
Action: Deploy to staging before production
Verify: All tests pass, application works as expected
Best practice: Always test deployments in non-prod first

20. Check application logs post-deployment
Command: kubectl logs -f <pod-name> --tail=100
Look for: Startup errors, connection failures
Monitor: For at least 5 minutes after deployment

21. Verify load balancer and ingress
Command: kubectl get ingress -n production
Expected: Ingress configured correctly with valid hosts
Check: DNS resolution to correct IPs

22. Run smoke tests
Action: Execute automated smoke test suite
Verify: Critical user journeys work
Examples: Login, key API endpoints, database queries

23. Monitor application metrics
Tools: Prometheus, Grafana, DataDog, New Relic
Check: Response times, error rates, throughput
Alert: If metrics degrade after deployment

24. Document the issue and resolution
Action: Create incident report
Include: Root cause, resolution steps, prevention measures
Update: Deployment runbook with lessons learned"""
        ),
        (
            "Memory Leak Issues",
            "performance",
            "memory leak,high memory,out of memory,oom,memory usage,heap,ram full,memory exhausted,gc issues",
            """1. Check current memory usage
Command: free -h
Look for: Available memory vs total
Critical: If available < 10% of total
Command: top -o %MEM (sort by memory)

2. Identify memory-consuming processes
Command: ps aux --sort=-%mem | head -20
Action: Note top 5 processes by memory usage
Check: Are these expected processes?

3. Check for Out of Memory (OOM) events
Command: dmesg | grep -i "out of memory"
Or: journalctl -k | grep -i "oom"
Look for: Killed processes, OOM killer invocations

4. Monitor memory usage over time
Command: watch -n 2 'free -h'
Or: vmstat 5 (updates every 5 seconds)
Action: Observe if memory keeps increasing
Pattern: Steady increase = likely memory leak

5. Analyze Java heap usage (if Java application)
Command: jmap -heap <PID>
Expected: Used heap vs max heap
Warning: If consistently near max, heap leak likely
Action: Generate heap dump for analysis

6. Generate Java heap dump
Command: jmap -dump:format=b,file=heapdump.hprof <PID>
Or: jcmd <PID> GC.heap_dump heapdump.hprof
Tool: Analyze with Eclipse MAT or VisualVM
Look for: Objects not being garbage collected

7. Check Python memory usage (if Python application)
Tool: memory_profiler or tracemalloc
Command: python -m memory_profiler script.py
Or use: objgraph to find object references
Look for: Growing collections, unclosed resources

8. Monitor Node.js memory (if Node application)
Command: node --inspect app.js
Tool: Chrome DevTools for heap snapshot
Or: Use clinic.js for memory profiling
Look for: Event listener leaks, large buffers

9. Check for file descriptor leaks
Command: lsof -p <PID> | wc -l
Expected: Reasonable count (< 1000 usually)
If high: Application not closing files/connections
Action: Review code for unclosed resources

10. Analyze database connection pools
Check: Application connection pool configuration
Common issue: Connections not being released
Command: Check DB active connections
Action: Ensure proper connection.close() in code

11. Review recent code changes
Command: git log --since="1 week ago" --oneline
Action: Identify new features or changes
Look for: New caching, collections, or background tasks

12. Check cache sizes and eviction policies
Review: Redis, Memcached, or in-memory cache configs
Action: Verify TTL (time-to-live) is set
Check: Max memory limits and eviction policies
Example: maxmemory-policy in Redis

13. Monitor garbage collection activity
Java: jstat -gc <PID> 1000 (every 1 second)
Look for: Frequent full GCs, long GC pauses
If excessive: Tune GC parameters or reduce heap usage

14. Check for circular references
Action: Review object relationships in code
Common: Event listeners, callbacks, closures
Tool: Use memory profilers to find reference chains

15. Restart application as temporary fix
Command: systemctl restart application
Or: kubectl rollout restart deployment/<name>
Warning: This is temporary, leak will return
Action: Use time to investigate root cause

16. Implement memory limits (containers)
Kubernetes: Set memory limits in deployment.yaml
Docker: Use --memory flag
Example: memory: 2Gi (request), 4Gi (limit)
Benefit: Prevents single app from consuming all memory

17. Enable detailed logging temporarily
Action: Increase log level to DEBUG
Monitor: Object creation, connection opens/closes
Warning: This increases memory usage itself
Remember: Revert to INFO after analysis

18. Check for zombie threads
Command: ps -eLf | grep <process-name> | wc -l
Expected: Reasonable thread count
If excessive: Thread leak, threads not terminating
Action: Review thread pool configuration

19. Review third-party library updates
Action: Check if recent library updates introduced leaks
Tool: Check library issue trackers on GitHub
Consider: Downgrade to previous stable version

20. Implement circuit breakers
Purpose: Prevent cascading failures
Action: Add timeout and retry limits
Libraries: Resilience4j (Java), Polly (.NET)
Benefit: Prevents connection/resource accumulation

21. Add memory profiling in production
Tools: 
- Java: JVisualVM, YourKit, JProfiler
- Python: memory_profiler, Py-Spy
- Node: clinic.js, 0x
Action: Profile with minimal overhead
Warning: Some profilers can affect performance

22. Set up memory alerts
Tool: Prometheus with alertmanager
Metric: container_memory_usage_bytes
Alert: When memory > 80% of limit
Action: Get notified before OOM occurs

23. Optimize data structures
Review: Large collections, lists, maps
Action: Use appropriate data structures
Examples:
- Use generators instead of lists (Python)
- Use weak references where appropriate
- Implement pagination for large datasets

24. Document and create prevention plan
Action: Create incident report
Include: Root cause analysis, code fixes applied
Prevention: Add memory tests to CI/CD
Future: Regular memory profiling in staging"""
        )
    ]
    
    cursor.executemany("""
        INSERT INTO runbooks (title, category, keywords, steps)
        VALUES (?, ?, ?, ?)
    """, runbooks)
    
    conn.commit()
    
    # Verify insertion
    cursor.execute("SELECT id, title, category FROM runbooks")
    rows = cursor.fetchall()
    
    print(f"\n✓ Successfully created {len(rows)} runbooks:")
    for row in rows:
        print(f"  {row[0]}. {row[1]} ({row[2]})")
    
    conn.close()
    print("\n✓ Database setup complete! File: runbooks.db")

if __name__ == "__main__":
    setup_database()