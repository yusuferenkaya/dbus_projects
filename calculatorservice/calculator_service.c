#include <gio/gio.h>
#include <stdlib.h>

static const gchar introspection_xml[] =
  "<node>"
  "  <interface name='calculator.service'>"
  "    <method name='Add'>"
  "      <arg type='d' name='a' direction='in'/>"
  "      <arg type='d' name='b' direction='in'/>"
  "      <arg type='d' name='result' direction='out'/>"
  "    </method>"
  "    <method name='Subtract'>"
  "      <arg type='d' name='a' direction='in'/>"
  "      <arg type='d' name='b' direction='in'/>"
  "      <arg type='d' name='result' direction='out'/>"
  "    </method>"
  "    <method name='Multiply'>"
  "      <arg type='d' name='a' direction='in'/>"
  "      <arg type='d' name='b' direction='in'/>"
  "      <arg type='d' name='result' direction='out'/>"
  "    </method>"
  "    <method name='Divide'>"
  "      <arg type='d' name='a' direction='in'/>"
  "      <arg type='d' name='b' direction='in'/>"
  "      <arg type='d' name='result' direction='out'/>"
  "    </method>"
  "    <property type='as' name='History' access='read'/>"
  "    <property type='d' name='LastOperationResult' access='read'/>"
  "  </interface>"
  "</node>";

typedef struct {
    GList *history;
    gdouble last_result;
} Calculator;

static GDBusNodeInfo *introspection_data = NULL;
static Calculator calculator = { NULL, 0.0 };

/* Method Call Handler */
static void
handle_method_call (GDBusConnection       *connection,
                    const gchar           *sender,
                    const gchar           *object_path,
                    const gchar           *interface_name,
                    const gchar           *method_name,
                    GVariant              *parameters,
                    GDBusMethodInvocation *invocation,
                    gpointer               user_data)
{
    gdouble a, b, result;
    gchar *entry;

    if (g_strcmp0(method_name, "Add") == 0) {
        g_variant_get(parameters, "(dd)", &a, &b);
        result = a + b;
        entry = g_strdup_printf("Added %g + %g = %g", a, b, result);
    } else if (g_strcmp0(method_name, "Subtract") == 0) {
        g_variant_get(parameters, "(dd)", &a, &b);
        result = a - b;
        entry = g_strdup_printf("Subtracted %g - %g = %g", a, b, result);
    } else if (g_strcmp0(method_name, "Multiply") == 0) {
        g_variant_get(parameters, "(dd)", &a, &b);
        result = a * b;
        entry = g_strdup_printf("Multiplied %g * %g = %g", a, b, result);
    } else if (g_strcmp0(method_name, "Divide") == 0) {
        g_variant_get(parameters, "(dd)", &a, &b);
        if (b == 0) {
            g_dbus_method_invocation_return_error(invocation, G_IO_ERROR, G_IO_ERROR_FAILED, "Division by zero");
            return;
        }
        result = a / b;
        entry = g_strdup_printf("Divided %g / %g = %g", a, b, result);
    } else {
        return;
    }

    calculator.history = g_list_append(calculator.history, entry);
    calculator.last_result = result;

    /* Emit PropertiesChanged signal for LastOperationResult */
    GVariantBuilder *builder = g_variant_builder_new(G_VARIANT_TYPE_ARRAY);
    g_variant_builder_add(builder, "{sv}", "LastOperationResult", g_variant_new_double(calculator.last_result));

    g_dbus_connection_emit_signal(connection,
                                  NULL,
                                  object_path,
                                  "org.freedesktop.DBus.Properties",
                                  "PropertiesChanged",
                                  g_variant_new("(sa{sv}as)", "calculator.service", builder, NULL),
                                  NULL);
    g_variant_builder_unref(builder);

    g_dbus_method_invocation_return_value(invocation, g_variant_new("(d)", result));
}

/* Property Handler */
static GVariant *
handle_get_property (GDBusConnection  *connection,
                     const gchar      *sender,
                     const gchar      *object_path,
                     const gchar      *interface_name,
                     const gchar      *property_name,
                     GError          **error,
                     gpointer          user_data)
{
    GVariant *ret = NULL;
    
    if (g_strcmp0(property_name, "History") == 0) {
        gchar **history_array = g_malloc0((g_list_length(calculator.history) + 1) * sizeof(gchar *));
        GList *iter = calculator.history;
        gint i = 0;

        while (iter != NULL) {
            history_array[i++] = g_strdup(iter->data);
            iter = g_list_next(iter);
        }
        
        ret = g_variant_new_strv((const gchar * const *)history_array, -1);
        g_strfreev(history_array);
    } else if (g_strcmp0(property_name, "LastOperationResult") == 0) {
        ret = g_variant_new_double(calculator.last_result);
    }

    return ret;
}

static const GDBusInterfaceVTable interface_vtable = {
    handle_method_call,
    handle_get_property,
    NULL
};

/* Called when bus is acquired */
static void
on_bus_acquired (GDBusConnection *connection,
                 const gchar     *name,
                 gpointer         user_data)
{
    guint registration_id;

    registration_id = g_dbus_connection_register_object (connection,
                                                         "/calculator/service",
                                                         introspection_data->interfaces[0],
                                                         &interface_vtable,
                                                         NULL,  /* user_data */
                                                         NULL,  /* user_data_free_func */
                                                         NULL); /* GError** */
    g_assert (registration_id > 0);
}

static void
on_name_acquired (GDBusConnection *connection,
                  const gchar     *name,
                  gpointer         user_data)
{
}

static void
on_name_lost (GDBusConnection *connection,
              const gchar     *name,
              gpointer         user_data)
{
  exit (1);
}

int
main (int argc, char *argv[])
{
    guint owner_id;
    GMainLoop *loop;

    g_type_init ();

    introspection_data = g_dbus_node_info_new_for_xml (introspection_xml, NULL);
    g_assert (introspection_data != NULL);

    owner_id = g_bus_own_name (G_BUS_TYPE_SESSION,
                               "calculator.service",
                               G_BUS_NAME_OWNER_FLAGS_NONE,
                               on_bus_acquired,
                               on_name_acquired,
                               on_name_lost,
                               NULL,
                               NULL);

    loop = g_main_loop_new (NULL, FALSE);
    g_main_loop_run (loop);

    /* Clean */
    g_bus_unown_name (owner_id);
    g_dbus_node_info_unref (introspection_data);

    return 0;
}