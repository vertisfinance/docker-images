import net from 'net';


const server = net.createServer();

server.on('listening', () => {
  const {address, port} = server.address();
  console.log(`listening on ${address}:${port}`);
});

server.on('connection', (socket) => {
  const rA = socket.remoteAddress;
  const rP = socket.remotePort;
  console.log(`connected ${rA}:${rP}`);

  socket.setEncoding('utf8');
  socket.setTimeout(5000);

  socket.on('data', (data) => {
    const lines = data.trim().split(/\r?\n/);
    lines.map((l) => socket.write(`${l}${l}\n`));
  });

  socket.on('close', () => {
    console.log('close');
  });

  socket.on('error', () => {
    console.log('error, will destroy');
    socket.destroy();
  });

  socket.on('timeout', () => {
    console.log('timeout, will destroy');
    socket.destroy();
  });
});

server.listen(8194, '0.0.0.0');
