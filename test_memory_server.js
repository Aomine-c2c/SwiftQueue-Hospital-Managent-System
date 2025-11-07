import { spawn } from 'child_process';

async function testMemoryServer() {
  return new Promise((resolve, reject) => {
    const server = spawn('node', ['C:\\Users\\armut\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-memory\\dist\\index.js'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    server.stdout.on('data', (data) => {
      output += data.toString();
    });

    server.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    // Wait a bit for server to start
    setTimeout(() => {
      // Send initialize request
      const initRequest = {
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {},
          clientInfo: {
            name: 'test-client',
            version: '1.0.0'
          }
        }
      };

      server.stdin.write(JSON.stringify(initRequest) + '\n');

      // Wait for response and then send tools/list
      setTimeout(() => {
        const listToolsRequest = {
          jsonrpc: '2.0',
          id: 2,
          method: 'tools/list',
          params: {}
        };

        server.stdin.write(JSON.stringify(listToolsRequest) + '\n');

        // Wait for response and then call create_entities
        setTimeout(() => {
          const createEntitiesRequest = {
            jsonrpc: '2.0',
            id: 3,
            method: 'tools/call',
            params: {
              name: 'create_entities',
              arguments: {
                entities: [
                  {
                    name: 'John_Doe',
                    entityType: 'person',
                    observations: ['Software Engineer', 'Lives in San Francisco']
                  }
                ]
              }
            }
          };

          server.stdin.write(JSON.stringify(createEntitiesRequest) + '\n');

          // Wait for response and then call read_graph
          setTimeout(() => {
            const readGraphRequest = {
              jsonrpc: '2.0',
              id: 4,
              method: 'tools/call',
              params: {
                name: 'read_graph',
                arguments: {}
              }
            };

            server.stdin.write(JSON.stringify(readGraphRequest) + '\n');

            // Wait for final response
            setTimeout(() => {
              server.kill();
              console.log('Server output:', output);
              console.log('Server errors:', errorOutput);
              resolve({ output, errorOutput });
            }, 2000);
          }, 2000);
        }, 2000);
      }, 2000);
    }, 2000);
  });
}

testMemoryServer().then((result) => {
  console.log('Test completed');
}).catch((error) => {
  console.error('Test failed:', error);
});
