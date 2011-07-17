from zope.component import adapts, provideAdapter

from opennode.oms.endpoint.occi.base import HttpRestView
from opennode.oms.model.root import Root, ComputeList, Compute


class RootView(HttpRestView):
    adapts(Root)

    def render(self, request, store):
        return None


class ComputeListView(HttpRestView):
    adapts(ComputeList)

    def render(self, request, store):
        return [{'name': compute} for compute in self.context.get_all()]


class ComputeView(HttpRestView):
    adapts(Compute)

    def render(self, request, store):
        return {'name': str(self.context)}


provideAdapter(RootView)
provideAdapter(ComputeListView)
provideAdapter(ComputeView)



#~ # TODO: Move to a future config file/module.
#~ DEBUG = True


#~ class ComputeListResource(resource.Resource):

#~     def __init__(self, avatar=None):
#~         ## Twisted Resource is a not a new style class, so emulating a super-call
#~         resource.Resource.__init__(self)

#~         # TODO: This should be handled generically.
#~         self.avatar = avatar

#~     def getChild(self, path, request):
#~         # TODO: This should be handled generically.
#~         if not path: return self  # For trailing slahses.

#~         # TODO: This should be handled generically.
#~         return ComputeItemResource(path, avatar=self.avatar)

#~     def render_POST(self, request):
#~         # TODO: This should be handled generically.
#~         data = dict((k, request.args.get(k, [None])[0])
#~                     for k in ['name', 'hostname', 'ip', 'category'])
#~         deferred = ComputeBO().create_compute(data)

#~         @deferred
#~         def on_success((success, ret)):
#~             if success:
#~                 request.setResponseCode(201, 'Created')
#~                 request.setHeader('Location', ret)
#~             else:
#~                 request.setResponseCode(400, 'Bad Request')
#~             request.finish()

#~         @deferred
#~         def on_error(failure):
#~             failure = str(failure)
#~             log.err("Failed to create Compute", failure)
#~             request.setResponseCode(500, 'Server Error')
#~             if DEBUG: request.write(failure)
#~             request.finish()

#~         return NOT_DONE_YET


#~     def render_GET(self, request):
#~         deferred = ComputeBO().get_compute_all_basic()

#~         @deferred
#~         def on_success(info):
#~             request.write(json.dumps(info, indent=2) + '\n')
#~             request.finish()

#~         @deferred
#~         def on_error(failure):
#~             failure = str(failure)
#~             log.err("Failed to retrieve Compute list", failure)
#~             request.setResponseCode(500, 'Server Error')
#~             if DEBUG: request.write(failure)
#~             request.finish()

#~         return NOT_DONE_YET


#~ class ComputeItemResource(resource.Resource):

#~     def __init__(self, compute_id, avatar):
#~         resource.Resource.__init__(self)
#~         # TODO: This should be handled generically.
#~         self.avatar = avatar
#~         try:
#~             self.compute_id = int(compute_id)
#~         except ValueError:
#~             self.compute_id = None

#~     def getChild(self, path, request):
#~         # TODO: This should be handled generically.
#~         if not path: return self  # For trailing slahses.

#~         # TODO: This should be handled generically.
#~         self.compute_id = None
#~         return self

#~     def render_GET(self, request):
#~         # TODO: This should be handled generically.
#~         if self.compute_id is None:
#~             request.setResponseCode(404, 'Not Found')
#~             return ''

#~         deferred = ComputeBO().get_compute_one_basic(self.compute_id)

#~         @deferred
#~         def on_success(info):
#~             if not info:
#~                 request.setResponseCode(404, 'Not Found')
#~                 request.finish()
#~             else:
#~                 #~ request.setHeader('Content-Type', 'application/x-json')
#~                 #~ request.setHeader('Content-length', len(json.dumps(info) + '\n'))
#~                 request.write(json.dumps(info, indent=2) + '\n')
#~                 request.finish()

#~         @deferred
#~         def on_error(failure):
#~             failure = str(failure)
#~             log.err("Failed to retrieve Compute with ID %s" % self.compute_id, failure)
#~             request.setResponseCode(500, 'Server Error')
#~             if DEBUG: request.write(failure)
#~             request.finish()

#~         return NOT_DONE_YET
