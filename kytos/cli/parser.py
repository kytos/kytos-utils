
def parse(doc, argv):
  args = docopt(doc, argv=argv)
  func = getattr(NappsManager, args['<subcommand>'], args['<napp>'])
  func(napps)
