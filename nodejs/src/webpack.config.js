module.exports = {
  entry: [
    './app.js'
  ],
  output: {
    filename: 'build.js'
  },
  loaders: [
    {
      test: /\.js$/,
      exclude: /node_modules/,
      loader: 'babel',
      query: {
        presets: ['es2015', 'stage-2']
      }
    }
  ]
};
